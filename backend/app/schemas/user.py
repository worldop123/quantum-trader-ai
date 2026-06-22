from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    theme: Optional[str] = None
    language: Optional[str] = None
    rise_color: Optional[str] = None
    fall_color: Optional[str] = None
    notification_enabled: Optional[bool] = None
    pushplus_token: Optional[str] = None


class UserSettings(BaseModel):
    theme: str = "dark"
    language: str = "zh"
    rise_color: str = "#00ff88"
    fall_color: str = "#ff4757"
    notification_enabled: bool = True


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    theme: str
    language: str
    rise_color: str
    fall_color: str
    notification_enabled: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
