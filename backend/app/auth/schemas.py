from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re
from ..utils.phone import is_valid_phone_number, format_phone_number

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    phone: Optional[str] = None
    terms_accepted: bool = False

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v):
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('terms_accepted')
    @classmethod
    def validate_terms_accepted(cls, v):
        if not v:
            raise ValueError('You must accept the Terms of Service and Privacy Policy')
        return v

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone_format(cls, v):
        if v is None:
            return v
        # Remove any spaces or dashes for validation
        cleaned_phone = v.replace(' ', '').replace('-', '')
        if not is_valid_phone_number(cleaned_phone):
            raise ValueError('Phone number must be in international format (e.g., +919876543210)')
        # format_phone_number now returns the number without the leading +
        return format_phone_number(cleaned_phone)

class UserLogin(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
