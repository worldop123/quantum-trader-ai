from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, APIKey
from app.schemas import UserUpdate, UserResponse, APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyVerifyResponse
from app.services import get_current_user
from app.utils.encryption import encrypt, decrypt, mask_api_key
from app.services.okx_service import OKXService

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/settings", response_model=UserResponse)
async def get_settings(current_user: User = Depends(get_current_user)):
    """获取用户设置"""
    return current_user


@router.put("/settings", response_model=UserResponse)
async def update_settings(
    settings_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户设置"""
    update_data = settings_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return current_user


# ========== API密钥管理 ==========

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户API密钥列表"""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()

    # 转换为响应格式（脱敏）
    result = []
    for key in api_keys:
        decrypted_key = decrypt(key.encrypted_api_key)
        result.append(APIKeyResponse(
            id=key.id,
            name=key.name,
            exchange=key.exchange,
            api_key_masked=mask_api_key(decrypted_key),
            is_demo=key.is_demo,
            is_active=key.is_active,
            last_verified_at=key.last_verified_at,
            created_at=key.created_at
        ))

    return result


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建API密钥"""
    # 加密存储
    encrypted_api_key = encrypt(key_data.api_key)
    encrypted_api_secret = encrypt(key_data.api_secret)
    encrypted_passphrase = encrypt(key_data.passphrase) if key_data.passphrase else None

    new_key = APIKey(
        user_id=current_user.id,
        name=key_data.name,
        exchange=key_data.exchange,
        encrypted_api_key=encrypted_api_key,
        encrypted_api_secret=encrypted_api_secret,
        encrypted_passphrase=encrypted_passphrase,
        is_demo=key_data.is_demo,
    )

    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    return APIKeyResponse(
        id=new_key.id,
        name=new_key.name,
        exchange=new_key.exchange,
        api_key_masked=mask_api_key(key_data.api_key),
        is_demo=new_key.is_demo,
        is_active=new_key.is_active,
        last_verified_at=new_key.last_verified_at,
        created_at=new_key.created_at
    )


@router.put("/api-keys/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: int,
    key_data: APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新API密钥"""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API密钥不存在"
        )

    update_data = key_data.model_dump(exclude_unset=True)

    # 处理需要加密的字段
    if "api_key" in update_data:
        api_key.encrypted_api_key = encrypt(update_data.pop("api_key"))
    if "api_secret" in update_data:
        api_key.encrypted_api_secret = encrypt(update_data.pop("api_secret"))
    if "passphrase" in update_data:
        api_key.encrypted_passphrase = encrypt(update_data.pop("passphrase")) if update_data["passphrase"] else None

    for key, value in update_data.items():
        setattr(api_key, key, value)

    db.commit()
    db.refresh(api_key)

    decrypted_key = decrypt(api_key.encrypted_api_key)
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        exchange=api_key.exchange,
        api_key_masked=mask_api_key(decrypted_key),
        is_demo=api_key.is_demo,
        is_active=api_key.is_active,
        last_verified_at=api_key.last_verified_at,
        created_at=api_key.created_at
    )


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除API密钥"""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API密钥不存在"
        )

    db.delete(api_key)
    db.commit()

    return {"success": True, "message": "删除成功"}


@router.post("/api-keys/{key_id}/verify", response_model=APIKeyVerifyResponse)
async def verify_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """验证API密钥"""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API密钥不存在"
        )

    # 解密密钥
    decrypted_api_key = decrypt(api_key.encrypted_api_key)
    decrypted_api_secret = decrypt(api_key.encrypted_api_secret)
    decrypted_passphrase = decrypt(api_key.encrypted_passphrase) if api_key.encrypted_passphrase else None

    # 创建服务实例验证
    service = OKXService(
        api_key=decrypted_api_key,
        api_secret=decrypted_api_secret,
        passphrase=decrypted_passphrase,
        is_demo=api_key.is_demo
    )

    result = await service.verify_api_key()

    if result["success"]:
        from datetime import datetime
        api_key.last_verified_at = datetime.utcnow()
        api_key.is_active = True
        db.commit()

    return APIKeyVerifyResponse(
        success=result["success"],
        message=result["message"],
        balance=None
    )
