from sqlalchemy.orm import Session
from . import models, schemas, security
from typing import Optional

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

async def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.get(models.User, user_id)

async def create_user(db: Session, email: str, password_hash: str, phone: str = None):
    # Note: caller should handle hashing
    db_user = models.User(
        email=email,
        password_hash=password_hash,
        phone=phone
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

# Adapter for older calls if necessary (though we refactored routes)
# Keeping create_user generic signature match if needed by other modules
# But we changed signature to match the new routes usage.