from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session
from .models import User
import secrets

# These should ideally come from env vars
SECRET_KEY = "your_access_token_secret_here"
REFRESH_SECRET_KEY = "your_refresh_token_secret_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> Tuple[bool, Optional[str]]:
    """
    Verify password and return (is_valid, new_hash).
    Argon2 automatically handles salt and rehashing if parameters change.
    """
    try:
        ph.verify(hashed_password, plain_password)
        # Check if rehash is needed
        if ph.check_needs_rehash(hashed_password):
            return True, ph.hash(plain_password)
        return True, None
    except VerifyMismatchError:
        return False, None
    except Exception:
        return False, None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_csrf_token():
    return secrets.token_urlsafe(32)

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
    db.commit()
    
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
        db.commit()
        return user.failed_login_attempts, user.locked_until
    
    db.commit()
    return user.failed_login_attempts, None


async def record_successful_login(db: Session, user: User):
    """
    Record successful login and reset failed attempts.
    """
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_failed_attempt = None
    user.last_login = datetime.utcnow()
    db.commit()