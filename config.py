# Flask Configuration
import os
from typing import Dict, Any


class Config:
    """Base configuration class"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-for-testing"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Authentication configuration
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    GITHUB_OAUTH_CLIENT_ID = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
    GITHUB_OAUTH_CLIENT_SECRET = os.environ.get("GITHUB_OAUTH_CLIENT_SECRET")
    OKTA_OAUTH_CLIENT_ID = os.environ.get("OKTA_OAUTH_CLIENT_ID")
    OKTA_OAUTH_CLIENT_SECRET = os.environ.get("OKTA_OAUTH_CLIENT_SECRET")
    OKTA_ORG = os.environ.get("OKTA_ORG")
    COGNITO_OAUTH_CLIENT_ID = os.environ.get("COGNITO_OAUTH_CLIENT_ID")
    COGNITO_OAUTH_CLIENT_SECRET = os.environ.get("COGNITO_OAUTH_CLIENT_SECRET")
    COGNITO_REGION = os.environ.get("COGNITO_REGION")
    COGNITO_USER_POOL = os.environ.get("COGNITO_USER_POOL")
    # Local registration configuration
    LOCAL_REGISTRATION_ENABLED = (
        os.environ.get("LOCAL_REGISTRATION_ENABLED", "True").lower() == "true"
    )


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False


# Configuration dictionary
config: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
