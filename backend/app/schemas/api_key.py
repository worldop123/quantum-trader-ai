from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    exchange: str = Field(..., description="交易所类型: okx/binance/...")
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    is_demo: bool = True


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    is_demo: Optional[bool] = None
    is_active: Optional[bool] = None


class APIKeyResponse(BaseModel):
    id: int
    name: str
    exchange: str
    api_key_masked: str  # 脱敏后的API Key
    is_demo: bool
    is_active: bool
    last_verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyVerifyResponse(BaseModel):
    success: bool
    message: str
    balance: Optional[float] = None
