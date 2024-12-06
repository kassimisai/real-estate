from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str

    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    VAPI_API_KEY: Optional[str] = None
    DOCUSIGN_API_KEY: Optional[str] = None

    # Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Google Calendar
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
