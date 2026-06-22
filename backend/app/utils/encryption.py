import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.config import settings


def get_fernet() -> Fernet:
    """获取加密器实例"""
    password = settings.ENCRYPTION_KEY.encode()
    salt = b"quantum_trader_salt_2024"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return Fernet(key)


def encrypt(data: str) -> str:
    """加密字符串"""
    if not data:
        return data
    f = get_fernet()
    return f.encrypt(data.encode()).decode()


def decrypt(encrypted_data: str) -> str:
    """解密字符串"""
    if not encrypted_data:
        return encrypted_data
    f = get_fernet()
    return f.decrypt(encrypted_data.encode()).decode()


def mask_api_key(api_key: str, show_first: int = 4, show_last: int = 4) -> str:
    """脱敏显示API密钥，只显示前几位和后几位"""
    if not api_key:
        return ""
    if len(api_key) <= show_first + show_last:
        return "*" * len(api_key)
    return api_key[:show_first] + "*" * (len(api_key) - show_first - show_last) + api_key[-show_last:]
