Models and email_service is done

1. Add email verification flow:
   - Generate a time-limited verification token on sign-up
   - Send a verification email with a secure link
   - Only activate the account after verification
2. account lockout
basically after 5 incorrect tries in password, there should be a lockout of the account for 15-30 mins. 
these need to be added

I'll add both email verification and account lockout features with industry-standard security practices.

## Updated Database Models

**`backend/auth/models.py`** (Updated)
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # OAuth fields
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    
    # Security fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification status
    
    # Account lockout fields
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_failed_attempt = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_login = Column(DateTime, nullable=True)


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(128), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
```

## Email Service

**`backend/services/email_service.py`**
```python
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
import httpx
from sqlalchemy.orm import Session
from auth.models import EmailVerificationToken

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@yourdomain.com")
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")


async def generate_verification_token(db: Session, user_id: int) -> str:
    """
    Generate a secure 128-character verification token.
    Token expires in 24 hours.
    """
    # Generate cryptographically secure random token
    token = secrets.token_urlsafe(96)  # 96 bytes = 128 characters base64url
    
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # Store token in database
    verification_token = EmailVerificationToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(verification_token)
    await db.commit()
    
    return token


async def send_verification_email(email: str, token: str) -> bool:
    """
    Send verification email using Resend API.
    Returns True if email sent successfully.
    """
    verification_link = f"{BASE_URL}/api/auth/verify-email?token={token}"
    
    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
            <h2 style="color: #2563eb; margin-top: 0;">Verify Your Email Address</h2>
            
            <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" 
                   style="background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Verify Email Address
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                This link will expire in 24 hours. If you didn't create an account, please ignore this email.
            </p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <span style="word-break: break-all;">{verification_link}</span>
            </p>
        </div>
    </body>
    </html>
    """
    
    email_text = f"""
    Verify Your Email Address
    
    Thank you for signing up! Please verify your email address by clicking the link below:
    
    {verification_link}
    
    This link will expire in 24 hours. If you didn't create an account, please ignore this email.
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": FROM_EMAIL,
                    "to": [email],
                    "subject": "Verify your email address",
                    "html": email_html,
                    "text": email_text
                },
                timeout=10.0
            )
            
            return response.status_code == 200
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


async def verify_email_token(db: Session, token: str) -> Optional[int]:
    """
    Verify email token and return user_id if valid.
    Returns None if token is invalid, expired, or already used.
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token == token,
            EmailVerificationToken.is_used == False
        )
    )
    
    verification_token = result.scalar_one_or_none()
    
    if not verification_token:
        return None
    
    # Check if token expired
    if datetime.utcnow() > verification_token.expires_at:
        return None
    
    # Mark token as used
    verification_token.is_used = True
    await db.commit()
    
    return verification_token.user_id


async def resend_verification_email(db: Session, user_id: int, email: str) -> bool:
    """
    Invalidate old tokens and send new verification email.
    """
    from sqlalchemy import update
    
    # Invalidate all previous tokens for this user
    await db.execute(
        update(EmailVerificationToken)
        .where(EmailVerificationToken.user_id == user_id)
        .values(is_used=True)
    )
    await db.commit()
    
    # Generate and send new token
    token = await generate_verification_token(db, user_id)
    return await send_verification_email(email, token)
```

## Updated Security Module

**`backend/auth/security.py`** (Add lockout functions)
```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from .models import User
import os

# ... (keep existing code) ...

# Account lockout configuration
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 20  # 20 minutes lockout


async def check_account_lockout(db: Session, user: User) -> Tuple[bool, Optional[int]]:
    """
    Check if account is locked out.
    Returns (is_locked, seconds_remaining)
    """
    if not user.locked_until:
        return False, None
    
    now = datetime.utcnow()
    
    if now < user.locked_until:
        # Account is still locked
        remaining = (user.locked_until - now).total_seconds()
        return True, int(remaining)
    
    # Lockout expired, reset the account
    user.locked_until = None
    user.failed_login_attempts = 0
    await db.commit()
    
    return False, None


async def record_failed_login(db: Session, user: User) -> Tuple[int, Optional[datetime]]:
    """
    Record a failed login attempt.
    Returns (attempts_count, locked_until)
    """
    user.failed_login_attempts += 1
    user.last_failed_attempt = datetime.utcnow()
    
    # Lock account if threshold reached
    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        await db.commit()
        return user.failed_login_attempts, user.locked_until
    
    await db.commit()
    return user.failed_login_attempts, None


async def record_successful_login(db: Session, user: User):
    """
    Record successful login and reset failed attempts.
    """
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_failed_attempt = None
    user.last_login = datetime.utcnow()
    await db.commit()
```

## Updated Routes

**`backend/auth/routes.py`** (Updated with verification and lockout)
```python
from fastapi import APIRouter, HTTPException, Response, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from .schemas import SignUpRequest, SignInRequest, TokenResponse
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
from services.email_service import (
    generate_verification_token,
    send_verification_email,
    verify_email_token,
    resend_verification_email
)
from database import get_db
import httpx
from urllib.parse import urlencode
import os

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/signup")
@limiter.limit("5/minute")
async def signup(
    request: Request,
    signup_data: SignUpRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Sign up new user with email and password.
    Sends verification email before account activation.
    """
    
    # Check if user exists
    existing_user = await get_user_by_email(db, signup_data.email)
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
    await db.commit()
    
    # Create session tokens
    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})
    
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
        url="/dashboard?verified=true",
        status_code=303
    )


@router.post("/resend-verification")
@limiter.limit("3/hour")  # Stricter rate limit for resend
async def resend_verification(
    request: Request,
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Resend verification email.
    Rate limited to prevent abuse.
    """
    
    user = await get_user_by_email(db, email)
    
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


@router.post("/signin")
@limiter.limit("10/minute")  # Higher limit but lockout handles security
async def signin(
    request: Request,
    signin_data: SignInRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Sign in with email and password.
    Implements account lockout after 5 failed attempts.
    """
    
    # Get user
    user = await get_user_by_email(db, signin_data.email)
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
    is_valid, new_hash = verify_password(signin_data.password, user.password_hash)
    
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
    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})
    
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
    
    return {"message": "Signed in successfully"}


# ... (keep existing Google OAuth and other routes) ...
```

## Updated DAL

**`backend/auth/dal.py`** (Add get_user_by_id)
```python
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from .models import User

# ... (keep existing functions) ...

async def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return await db.get(User, user_id)


async def mark_user_verified(db: Session, user_id: int):
    """Mark user email as verified"""
    user = await db.get(User, user_id)
    if user:
        user.is_verified = True
        user.is_active = True
        await db.commit()
```

## Frontend Components

**`components/auth/VerificationPending.tsx`**
```typescript
'use client';

import { useState } from 'react';

interface VerificationPendingProps {
  email: string;
}

export function VerificationPending({ email }: VerificationPendingProps) {
  const [resending, setResending] = useState(false);
  const [message, setMessage] = useState('');

  const handleResend = async () => {
    setResending(true);
    setMessage('');

    try {
      const response = await fetch('/api/auth/resend-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('Verification email sent! Please check your inbox.');
      } else {
        setMessage(data.error || 'Failed to resend email');
      }
    } catch (err) {
      setMessage('Failed to resend email. Please try again.');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
            <svg
              className="h-6 w-6 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Check your email
          </h2>
          
          <p className="mt-2 text-sm text-gray-600">
            We've sent a verification link to
            <br />
            <span className="font-medium text-gray-900">{email}</span>
          </p>
        </div>

        <div className="rounded-md bg-blue-50 p-4">
          <div className="text-sm text-blue-700">
            <p className="font-medium">Please verify your email to continue</p>
            <p className="mt-1">Click the link in the email to activate your account.</p>
          </div>
        </div>

        {message && (
          <div className={`rounded-md p-4 ${
            message.includes('sent') ? 'bg-green-50' : 'bg-red-50'
          }`}>
            <p className={`text-sm ${
              message.includes('sent') ? 'text-green-800' : 'text-red-800'
            }`}>
              {message}
            </p>
          </div>
        )}

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Didn't receive the email?{' '}
            <button
              onClick={handleResend}
              disabled={resending}
              className="font-medium text-blue-600 hover:text-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {resending ? 'Sending...' : 'Resend verification email'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
```

**`components/auth/SignUpForm.tsx`** (Updated to handle verification)
```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleOAuthButton } from './GoogleOAuthButton';
import { VerificationPending } from './VerificationPending';

export function SignUpForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showVerification, setShowVerification] = useState(false);

  // ... (keep existing validation and handleChange functions) ...

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          phone: formData.phone,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Sign up failed');
      }

      // Show verification pending screen
      setShowVerification(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign up failed');
    } finally {
      setLoading(false);
    }
  };

  if (showVerification) {
    return <VerificationPending email={formData.email} />;
  }

  // ... (keep existing form JSX) ...
}
```

## Database Migration

**`backend/alembic/versions/add_verification_lockout.py`**
```python
"""Add email verification and account lockout

Revision ID: 002
Revises: 001
Create Date: 2026-02-07

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add lockout and verification columns to users table
    op.add_column('users', sa.Column('last_failed_attempt', sa.DateTime(), nullable=True))
    
    # Create email_verification_tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=128), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_email_verification_tokens_token', 'email_verification_tokens', ['token'], unique=True)
    op.create_index('ix_email_verification_tokens_user_id', 'email_verification_tokens', ['user_id'])


def downgrade():
    op.drop_index('ix_email_verification_tokens_user_id', table_name='email_verification_tokens')
    op.drop_index('ix_email_verification_tokens_token', table_name='email_verification_tokens')
    op.drop_table('email_verification_tokens')
    op.drop_column('users', 'last_failed_attempt')
```

## Environment Variables (Updated)

**`.env`** (Add these)
```bash
# ... (keep existing variables) ...

# Email Service (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=noreply@yourdomain.com

# Base URL for verification links
BASE_URL=https://yourdomain.com
```

## Updated Dependencies

**`requirements.txt`** (Add)
```
fastapi>=0.109.0
argon2-cffi>=23.1.0
python-jose[cryptography]>=3.3.0
passlib>=1.7.4
slowapi>=0.1.9
httpx>=0.26.0
sqlalchemy>=2.0.0
alembic>=1.13.0
```

## Key Security Features

**Email Verification**: 128-character cryptographically secure tokens with 24-hour expiry prevent unauthorized account access [1][2]

**Token Security**: One-time use tokens stored securely in database, automatic invalidation of old tokens when resending [1][3]

**Account Lockout**: 5 failed attempts trigger 20-minute lockout period preventing brute-force attacks [4][5]

**Rate Limiting**: Stricter limits on verification email resends (3/hour) to prevent abuse [3]

**User Experience**: Clear feedback on remaining attempts before lockout, automatic lockout expiration [4]

The implementation follows 2026 security standards with proper token generation, secure email delivery via Resend [6][7], and progressive account protection [5].

Citations:
[1] Implementing the right email verification flow - SuperTokens https://supertokens.com/blog/implementing-the-right-email-verification-flow
[2] Demystifying Email Validation Tokens: Ensuring Secure and Accurate Verification https://blog.emaillistvalidation.com/blog/demystifying-email-validation-tokens-ensuring-secure-and-accurate-verification/
[3] Demystifying Email Verification Tokens: A Comprehensive Guide https://blog.emaillistvalidation.com/blog/demystifying-email-verification-tokens-a-comprehensive-guide/
[4] Implementing The Exponential Backoff Algorithm To Thwart ... https://community.f5.com/kb/technicalarticles/implementing-the-exponential-backoff-algorithm-to-thwart-dictionary-attacks/277295
[5] ory/kratos - Throttling repeated login requests & account lock - GitHub https://github.com/ory/kratos/issues/3037
[6] SendGrid vs. ReSend 2025⚠️Which Email Marketing Tool is Best? https://onehourprofessor.com/sendgrid-vs-resend/
[7] Resend vs SendGrid (2026) - Developer Email API ... https://www.sequenzy.com/versus/resend-vs-sendgrid
[8] 18 enterprise email security best practices for 2026 - TechTarget https://www.techtarget.com/searchsecurity/tip/2019s-top-email-security-best-practices-for-employees
[9] What Is Email Security? Best Practices for 2026 | UpGuard https://www.upguard.com/blog/email-security
[10] 10 Essential Email Security Best Practices for UK Businesses in 2026 https://www.f1group.com/email-security-best-practices/

