import os
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # App Settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "")

    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")

    # AWS Cognito Settings
    AWS_COGNITO_REGION: str = os.getenv("AWS_COGNITO_REGION", "us-east-1")
    AWS_COGNITO_USER_POOL_ID: str = os.getenv("AWS_COGNITO_USER_POOL_ID", "")
    AWS_COGNITO_CLIENT_ID: str = os.getenv("AWS_COGNITO_CLIENT_ID", "")
    
    # Authentication Settings
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "true").lower() == "true"

    # Zoho Integration
    ZOHO_CLIENT_ID: Optional[str] = os.getenv("ZOHO_CLIENT_ID")
    ZOHO_CLIENT_SECRET: Optional[str] = os.getenv("ZOHO_CLIENT_SECRET")
    ZOHO_REDIRECT_URI: Optional[str] = os.getenv("ZOHO_REDIRECT_URI")
    ZOHO_TOKEN_URL: str = os.getenv("ZOHO_TOKEN_URL", "https://accounts.zoho.in/oauth/v2/token")

    # QuickBooks Integration
    QUICKBOOKS_CLIENT_ID: Optional[str] = os.getenv("QUICKBOOKS_CLIENT_ID")
    QUICKBOOKS_CLIENT_SECRET: Optional[str] = os.getenv("QUICKBOOKS_CLIENT_SECRET")
    QUICKBOOKS_REDIRECT_URI: Optional[str] = os.getenv("QUICKBOOKS_REDIRECT_URI")
    QUICKBOOKS_TOKEN_URL: Optional[str] = os.getenv("QUICKBOOKS_TOKEN_URL")

    # Xero Integration
    XERO_CLIENT_ID: Optional[str] = os.getenv("XERO_CLIENT_ID")
    XERO_CLIENT_SECRET: Optional[str] = os.getenv("XERO_CLIENT_SECRET")
    XERO_REDIRECT_URI: Optional[str] = os.getenv("XERO_REDIRECT_URI")
    XERO_TOKEN_URL: Optional[str] = os.getenv("XERO_TOKEN_URL")

    @property
    def database_url(self) -> str:
        """Build SQLAlchemy DATABASE_URL from settings"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns the application settings as a singleton
    """
    return Settings()
