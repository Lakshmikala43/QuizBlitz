from datetime import datetime, timezone
from app.extensions import db


class Achievement(db.Model):
    """Badge or achievement that players can unlock."""

    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(64), default="trophy", nullable=False)
    tier = db.Column(db.String(16), default="bronze", nullable=False)  # bronze, silver, gold, platinum
    xp_reward = db.Column(db.Integer, default=100, nullable=False)
    coin_reward = db.Column(db.Integer, default=50, nullable=False)
    requirement_type = db.Column(db.String(64), nullable=False)  # matches_played, streak, score, correct_answers, daily_streak, level
    requirement_threshold = db.Column(db.Integer, default=1, nullable=False)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    player_achievements = db.relationship("PlayerAchievement", back_populates="achievement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Achievement {self.code} ({self.tier})>"

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "tier": self.tier,
            "xp_reward": self.xp_reward,
            "coin_reward": self.coin_reward,
            "requirement_type": self.requirement_type,
            "requirement_threshold": self.requirement_threshold,
        }


class PlayerAchievement(db.Model):
    """Record of an unlocked achievement for a player."""

    __tablename__ = "player_achievements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True)
    unlocked_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = db.relationship("User", back_populates="player_achievements")
    achievement = db.relationship("Achievement", back_populates="player_achievements")

    __table_args__ = (
        db.UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    def __repr__(self):
        return f"<PlayerAchievement user_id={self.user_id} achievement_id={self.achievement_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "achievement": self.achievement.to_dict() if self.achievement else None,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
        }
