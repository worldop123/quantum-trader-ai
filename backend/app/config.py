import os
from dotenv import load_dotenv
from typing import Optional, List

# 加载.env文件
load_dotenv()


class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quantum_trader.db")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "quantum-trader-secret-key-change-in-production-2024")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "quantum-trader-encryption-key-32chars!")

    # OKX Exchange
    OKX_API_KEY: Optional[str] = os.getenv("OKX_API_KEY")
    OKX_API_SECRET: Optional[str] = os.getenv("OKX_API_SECRET")
    OKX_PASSPHRASE: Optional[str] = os.getenv("OKX_PASSPHRASE")
    OKX_DEMO: bool = os.getenv("OKX_DEMO", "true").lower() == "true"

    # DeepSeek AI
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")

    # PushPlus Notification
    PUSHPLUS_TOKEN: Optional[str] = os.getenv("PUSHPLUS_TOKEN")
    PUSHPLUS_URL: str = os.getenv("PUSHPLUS_URL", "http://www.pushplus.plus/send")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", '["http://localhost:5173","http://localhost:3000"]').strip('[]').replace('"', '').split(',')


settings = Settings()
