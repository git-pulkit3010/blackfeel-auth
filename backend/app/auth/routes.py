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
    generate_csrf_token,
    check_account_lockout,
    record_failed_login,
    record_successful_login
)
from .dal import create_user, get_user_by_email, update_user_password, get_user_by_id
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
    """
    Sign up new user with email and password.
    Sends verification email before account activation.
    """
    
    # Check if user exists
    existing_user = get_user_by_email(db, signup_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(signup_data.password)
    
    # Create user (is_verified=False by default)
    user = await create_user(
        db,
        email=signup_data.email,
        password_hash=hashed_password,
        phone=signup_data.phone
    )
    
    # Generate verification token
    token = await generate_verification_token(db, user.id)
    
    # Send verification email in background
    background_tasks.add_task(send_verification_email, signup_data.email, token)
    
    return JSONResponse(
        status_code=201,
        content={
            "message": "Account created successfully. Please check your email to verify your account.",
            "user_id": user.id,
            "email_sent": True
        }
    )


@router.get("/verify-email")
async def verify_email(
    token: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Verify email address using token from email link.
    """
    
    # Verify token
    user_id = await verify_email_token(db, token)
    
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
    
    # Get user and mark as verified
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    user.is_active = True
    db.commit()
    
    # Create session tokens
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
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
    
    # Redirect to dashboard with success message
    return RedirectResponse(
        url="http://localhost:3000/dashboard?verified=true",
        status_code=303
    )


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
    success = await resend_verification_email(db, user.id, user.email)
    
    return {
        "message": "Verification email sent. Please check your inbox.",
        "email_sent": success
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
    
    return {"access_token": access_token, "token_type": "bearer"}