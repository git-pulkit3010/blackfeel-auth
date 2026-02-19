from fastapi import APIRouter, HTTPException, Response, Request, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from ..database import get_db
from . import schemas
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_csrf_token,
    check_account_lockout,
    record_failed_login,
    record_successful_login,
    verify_csrf,
    MAX_FAILED_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from .dal import (
    create_user,
    get_user_by_email,
    update_user_password,
    get_user_by_id,
    save_refresh_token,
    get_refresh_token,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens
)
from datetime import datetime, timedelta
from ..services.email_service import (
    generate_verification_token,
    send_verification_email,
    verify_email_token,
    resend_verification_email
)
import httpx
from urllib.parse import urlencode
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/signup")
@limiter.limit("5/minute")
async def signup(
    request: Request,
    signup_data: schemas.UserCreate,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing_user = get_user_by_email(db, signup_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists"
        )
    
    # Hash password
    hashed_password = hash_password(signup_data.password)
    
    # Create user (is_verified=False by default)
    user = await create_user(
        db,
        email=signup_data.email,
        password_hash=hashed_password,
        phone=signup_data.phone
    )
    
    # Generate the shared verification token
    token = await generate_verification_token(db, user.id)

    # Send verification email in the background
    background_tasks.add_task(send_verification_email, signup_data.email, token)

    csrf_token = generate_csrf_token()
    
    response = JSONResponse(
        status_code=201,
        content={
            "message": "Account created. Please check your email to verify your account.",
            "user_id": user.id,
            "verification_sent": {"email": True},
            "csrf_token": csrf_token
        }
    )
    
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False, # Must be accessible by frontend JS
        secure=True,
        samesite="lax",
        path="/"
    )

    return response

@router.get("/verify-email")
async def verify_email(
    token: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Verify email address using token from email link.
    """
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Verify token
    user_id, is_already_used = await verify_email_token(db, token)
    
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
    
    # Get user
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If already verified or token was already used, just redirect to dashboard
    if user.is_verified:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/dashboard?verified=already",
            status_code=303
        )
    
    user.is_verified = True
    user.is_active = True
    db.commit()
    
    # Create session tokens
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Save refresh token to DB
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    await save_refresh_token(db, user.id, refresh_token, expires_at)
    
    csrf_token = generate_csrf_token()
    
    # Redirect to dashboard with success message
    response = RedirectResponse(
        url=f"{FRONTEND_URL}/dashboard?verified=true",
        status_code=303
    )
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900,
        path="/"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=2592000,
        path="/api/auth/refresh"
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=True,
        samesite="lax",
        path="/"
    )
    
    return response


@router.post("/resend-verification")
@limiter.limit("3/hour")  # Stricter rate limit for resend
async def resend_verification(
    request: Request,
    email_data: schemas.UserBase, # expecting {email: ...}
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Resend verification email.
    Rate limited to prevent abuse.
    """
    email = email_data.email
    user = get_user_by_email(db, email)
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a verification link has been sent."}
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Resend verification email
    token = await generate_verification_token(db, user.id)
    background_tasks.add_task(send_verification_email, user.email, token)

    return {
        "message": "Verification link resent. Please check your email.",
        "email_sent": True
    }


@router.post("/signin", response_model=schemas.Token)
@limiter.limit("10/minute")  # Higher limit but lockout handles security
async def signin(
    request: Request,
    user_in: schemas.UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Sign in with email and password.
    Implements account lockout after 5 failed attempts.
    """

    # Get user
    user = get_user_by_email(db, user_in.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check account lockout
    is_locked, seconds_remaining = await check_account_lockout(db, user)
    if is_locked:
        minutes_remaining = int(seconds_remaining / 60) + 1
        raise HTTPException(
            status_code=429,
            detail=f"Account is locked due to too many failed login attempts. Try again in {minutes_remaining} minutes."
        )

    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email address before signing in. Check your inbox for the verification link."
        )

    # Verify password
    is_valid, new_hash = verify_password(user_in.password, user.password_hash)

    if not is_valid:
        # Record failed attempt
        attempts, locked_until = await record_failed_login(db, user)

        if locked_until:
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed login attempts. Account locked for {LOCKOUT_DURATION_MINUTES} minutes."
            )

        remaining_attempts = MAX_FAILED_ATTEMPTS - attempts
        raise HTTPException(
            status_code=401,
            detail=f"Invalid credentials. {remaining_attempts} attempts remaining before account lockout."
        )

    # Successful login - reset failed attempts
    await record_successful_login(db, user)

    # Rehash if needed (parameters updated)
    if new_hash:
        await update_user_password(db, user.id, new_hash)

    # Create tokens
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    # Save refresh token to DB
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    await save_refresh_token(db, user.id, refresh_token, expires_at)

    csrf_token = generate_csrf_token()

    # Create response
    response_content = {
        "access_token": access_token,
        "token_type": "bearer",
        "csrf_token": csrf_token
    }
    
    response = JSONResponse(content=response_content)

    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900,
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=2592000,
        path="/api/auth/refresh"
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=True,
        samesite="lax",
        path="/"
    )

    return response
    

@router.get("/callback/google")
async def google_callback(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    Exchange code for token, create/login user.
    """
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    
    # Determine redirect_uri based on Host header to match what frontend sent
    # We trust Host header because of Next.js rewriting
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    protocol = request.headers.get("x-forwarded-proto", "http")
    redirect_uri = f"{protocol}://{host}/api/auth/callback/google"
    
    if error:
        raise HTTPException(status_code=400, detail=f"Google Auth Error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
    
    # Get PKCE verifier from cookie
    code_verifier = request.cookies.get("pkce_code_verifier")
    
    # Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    # Include verifier if it exists (required for PKCE)
    if code_verifier:
        data["code_verifier"] = code_verifier
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get Token
            token_res = await client.post(token_url, data=data)
            if token_res.status_code != 200:
                 # Log the detailed error from Google for debugging
                 print(f"Google Token Error: {token_res.text}")
                 raise HTTPException(status_code=400, detail="Failed to retrieve Google token. The authorization code may have expired.")
            
            token_data = token_res.json()
            
            # Get User Info
            user_info_res = await client.get(f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token_data['access_token']}")
            user_info = user_info_res.json()
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection to Google timed out. Please try again.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to connect to Google: {str(e)}")
    
    # Check if user exists
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")
        
    user = get_user_by_email(db, email)
    
    if not user:
        # Register new user
        # We don't have password, so we set a random one or leave it null/unusable via password auth
        # For this example, we create user without password hash set (implicit social user)
        user = await create_user(
            db,
            email=email,
            password_hash=None, # Social login only
            phone=None # Ask for phone later if needed
        )
        user.is_verified = True # Google verified emails are trusted
        user.oauth_provider = "google"
        user.oauth_id = user_info.get("sub")
        db.commit()
    else:
        # Update existing user if needed, or link account
        if not user.oauth_provider:
            user.oauth_provider = "google"
            user.oauth_id = user_info.get("sub")
            if not user.is_verified:
                user.is_verified = True
            db.commit()

    # Login user
    await record_successful_login(db, user)
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Save refresh token to DB
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    await save_refresh_token(db, user.id, refresh_token, expires_at)
    
    csrf_token = generate_csrf_token()

    # Redirect to dashboard
    frontend_url = os.getenv("FRONTEND_URL", f"{protocol}://{host}")
    redirect_to = f"{frontend_url}/dashboard"
    
    resp = RedirectResponse(url=redirect_to, status_code=303)
    
    # Set cookies
    resp.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="lax", max_age=900, path="/")
    resp.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=2592000, path="/api/auth/refresh")
    resp.set_cookie(key="csrf_token", value=csrf_token, httponly=False, secure=True, samesite="lax", path="/")
    
    # Clear the PKCE cookie
    resp.delete_cookie("pkce_code_verifier", path="/")
    
    return resp

@router.post("/logout")
async def logout(
    response: Response, 
    request: Request, 
    db: Session = Depends(get_db),
    _ = Depends(verify_csrf)
):
    """
    Logout user by clearing cookies and revoking current refresh token.
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await revoke_refresh_token(db, refresh_token)

    response = JSONResponse(content={"message": "Successfully logged out"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    response.delete_cookie("csrf_token", path="/")
    return response

@router.post("/refresh")
@limiter.limit("20/minute")
async def refresh(
    request: Request, 
    db: Session = Depends(get_db),
    _ = Depends(verify_csrf)
):
    """
    Refresh access token using refresh token.
    Implements token rotation.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    # Verify refresh token in DB
    db_token = await get_refresh_token(db, refresh_token)
    if not db_token or db_token.is_revoked or db_token.expires_at < datetime.utcnow():
        if db_token and not db_token.is_revoked:
             # If it was a valid but expired token, just clean it
             await revoke_refresh_token(db, refresh_token)
        
        # If a revoked token is used, it might be an attack - revoke all user tokens
        if db_token and db_token.is_revoked:
            await revoke_all_user_refresh_tokens(db, db_token.user_id)
            
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Decode and verify JWT
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await get_user_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # TOKEN ROTATION
    # 1. Revoke old token
    await revoke_refresh_token(db, refresh_token)

    # 2. Create new tokens
    new_access_token = create_access_token({"sub": str(user.id), "email": user.email})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    # 3. Save new refresh token
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    await save_refresh_token(db, user.id, new_refresh_token, expires_at)

    response = JSONResponse(content={
        "access_token": new_access_token,
        "token_type": "bearer"
    })

    # Set new cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900,
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=2592000,
        path="/api/auth/refresh"
    )

    return response
