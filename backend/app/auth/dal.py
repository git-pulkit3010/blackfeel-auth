from sqlalchemy.orm import Session
from . import models, schemas, security
from ..utils.phone import format_phone_number
from typing import Optional
from datetime import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

async def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.get(models.User, user_id)

async def create_user(db: Session, email: str, password_hash: str, phone: str = None, terms_accepted: bool = False):
    # Note: caller should handle hashing
    # Format phone number to ensure it's in E.164 format before storing
    formatted_phone = format_phone_number(phone) if phone else None

    db_user = models.User(
        email=email,
        password_hash=password_hash,
        phone=formatted_phone,
        terms_accepted=terms_accepted,
        terms_accepted_at=datetime.utcnow() if terms_accepted else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

async def update_user_password(db: Session, user_id: int, new_hash: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.password_hash = new_hash
        db.commit()

async def mark_user_verified(db: Session, user_id: int):
    """Mark user email as verified"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_verified = True
        user.is_active = True
        db.commit()

# Refresh Token Management
async def save_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime):
    db_token = models.RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    return db_token

async def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()

async def revoke_refresh_token(db: Session, token: str):
    db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()

async def revoke_all_user_refresh_tokens(db: Session, user_id: int):
    db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user_id,
        models.RefreshToken.is_revoked == False
    ).update({"is_revoked": True}, synchronize_session=False)
    db.commit()

# Adapter for older calls if necessary (though we refactored routes)
# Keeping create_user generic signature match if needed by other modules
# But we changed signature to match the new routes usage.