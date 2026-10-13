import secrets
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """Core user and player entity."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(64), nullable=True)
    avatar_seed = db.Column(db.String(64), default="default", nullable=False)
    bio = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    reset_token = db.Column(db.String(100), nullable=True, index=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user_roles = db.relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    statistics = db.relationship("PlayerStatistics", back_populates="user", uselist=False, cascade="all, delete-orphan")
    quiz_sessions = db.relationship("QuizSession", back_populates="user", cascade="all, delete-orphan")
    match_results = db.relationship("MatchResult", back_populates="user", cascade="all, delete-orphan")
    player_achievements = db.relationship("PlayerAchievement", back_populates="user", cascade="all, delete-orphan")
    xp_transactions = db.relationship("XPTransaction", back_populates="user", cascade="all, delete-orphan")
    reward_transactions = db.relationship("RewardTransaction", back_populates="user", cascade="all, delete-orphan")
    room_participations = db.relationship("RoomParticipant", back_populates="user", cascade="all, delete-orphan")
    audit_logs = db.relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Hash and set the user's password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the password against the stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expires_in_minutes: int = 60) -> str:
        """Generate a cryptographically secure password reset token."""
        token = secrets.token_urlsafe(32)
        self.reset_token = token
        self.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        return token

    def verify_reset_token(self, token: str) -> bool:
        """Verify whether the reset token is valid and unexpired."""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if self.reset_token != token:
            return False
        now = datetime.now(timezone.utc)
        # Handle naive datetime comparison if needed
        expiry = self.reset_token_expiry
        if expiry.tzinfo is None:
            now = datetime.utcnow()
        return now <= expiry

    def clear_reset_token(self) -> None:
        """Invalidate the reset token."""
        self.reset_token = None
        self.reset_token_expiry = None

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specified role."""
        if self.is_admin and role_name in ("admin", "moderator", "player"):
            return True
        return any(ur.role.name == role_name for ur in self.user_roles if ur.role)

    @property
    def effective_display_name(self) -> str:
        """Return display name if set, otherwise username."""
        return self.display_name or self.username

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Serialize user to dict without exposing password hashes."""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "display_name": self.effective_display_name,
            "avatar_seed": self.avatar_seed,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        return data


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None
