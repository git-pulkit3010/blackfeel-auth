from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from ..utils.phone import is_valid_phone_number, format_phone_number

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    phone: Optional[str] = None
    
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
