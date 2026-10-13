import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Base application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "quiz-royale-dev-secret-key-change-in-production-random-token-998877"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'quiz_royale.db'}"
    )

    # Security & Sessions
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # Gameplay & Engine Tuning
    DEFAULT_QUESTION_TIME_LIMIT = int(os.environ.get("DEFAULT_QUESTION_TIME_LIMIT", 15))
    STREAK_BONUS_MULTIPLIER = float(os.environ.get("STREAK_BONUS_MULTIPLIER", 1.1))
    MAX_STREAK_CAP = int(os.environ.get("MAX_STREAK_CAP", 5))
    DAILY_CHALLENGE_QUESTIONS = int(os.environ.get("DAILY_CHALLENGE_QUESTIONS", 10))

    # Real-Time Multiplayer
    SOCKETIO_ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", "threading")
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"

    # WTForms / CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600


class DevelopmentConfig(BaseConfig):
    """Local development configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    """Test environment configuration."""

    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key-12345"


class ProductionConfig(BaseConfig):
    """Production deployment configuration."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    # Production database should be set via DATABASE_URL environment variable


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
