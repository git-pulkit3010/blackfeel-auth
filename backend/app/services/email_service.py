import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
import httpx
from sqlalchemy.orm import Session
from ..auth.models import EmailVerificationToken

# Ensure environment variables are loaded if not already
from dotenv import load_dotenv
load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
# Match the variable name in .env (RESEND_FROM_EMAIL)
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL") or os.getenv("FROM_EMAIL", "noreply@yourdomain.com")
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
    db.commit() # Synchronous commit for now as we are not using async session in this snippet context usually
    
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
        if not RESEND_API_KEY:
            print("Error: RESEND_API_KEY is missing in environment variables.")
            return False

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
            
            if response.status_code != 200:
                print(f"Resend API Error: {response.status_code} - {response.text}")
                return False

            return True
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


async def verify_email_token(db: Session, token: str) -> tuple[Optional[int], bool]:
    """
    Verify email token and return (user_id, is_already_used).
    Returns (None, False) if token is invalid or expired.
    """
    verification_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token
    ).first()
    
    if not verification_token:
        return None, False
    
    # Check if token expired
    if datetime.utcnow() > verification_token.expires_at:
        return None, False
    
    if verification_token.is_used:
        return verification_token.user_id, True
    
    # Mark token as used
    verification_token.is_used = True
    db.commit()
    
    return verification_token.user_id, False


async def resend_verification_email(db: Session, user_id: int, email: str) -> bool:
    """
    Invalidate old tokens and send new verification email.
    """
    from sqlalchemy import update
    
    # Invalidate all previous tokens for this user
    db.query(EmailVerificationToken).filter(EmailVerificationToken.user_id == user_id).update({"is_used": True})
    db.commit()
    
    # Generate and send new token
    token = await generate_verification_token(db, user_id)
    return await send_verification_email(email, token)
