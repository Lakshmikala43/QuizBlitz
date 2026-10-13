from datetime import datetime, timezone, date
from app.extensions import db


class DailyChallenge(db.Model):
    """Deterministic daily competitive challenge."""

    __tablename__ = "daily_challenges"

    id = db.Column(db.Integer, primary_key=True)
    challenge_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    bonus_xp = db.Column(db.Integer, default=250, nullable=False)
    bonus_coins = db.Column(db.Integer, default=100, nullable=False)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    attempts = db.relationship("DailyChallengeAttempt", back_populates="challenge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DailyChallenge {self.challenge_date}: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "challenge_date": self.challenge_date.isoformat() if self.challenge_date else None,
            "title": self.title,
            "description": self.description,
            "bonus_xp": self.bonus_xp,
            "bonus_coins": self.bonus_coins,
            "total_attempts": len(self.attempts),
        }


class DailyChallengeAttempt(db.Model):
    """A player's single ranked attempt at a daily challenge."""

    __tablename__ = "daily_challenge_attempts"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("daily_challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = db.Column(db.String(36), db.ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    accuracy_pct = db.Column(db.Float, default=0.0, nullable=False)
    completed_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    challenge = db.relationship("DailyChallenge", back_populates="attempts")
    user = db.relationship("User")
    session = db.relationship("QuizSession")

    # Strict constraint: only 1 recorded completion per player per daily challenge!
    __table_args__ = (
        db.UniqueConstraint("challenge_id", "user_id", name="uq_daily_user_attempt"),
    )

    def __repr__(self):
        return f"<DailyChallengeAttempt challenge_id={self.challenge_id} user_id={self.user_id} score={self.score}>"

    def to_dict(self):
        return {
            "id": self.id,
            "challenge_id": self.challenge_id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "Unknown",
            "display_name": self.user.effective_display_name if self.user else "Unknown",
            "avatar_seed": self.user.avatar_seed if self.user else "default",
            "score": self.score,
            "accuracy_pct": round(self.accuracy_pct, 1),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
