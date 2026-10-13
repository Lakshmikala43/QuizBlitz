from datetime import datetime, timezone
from app.extensions import db


class XPTransaction(db.Model):
    """Ledger recording every XP grant for anti-abuse auditing."""

    __tablename__ = "xp_transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    source_type = db.Column(db.String(32), nullable=False, index=True)  # match, achievement, daily_login, daily_challenge
    reference_id = db.Column(db.String(64), nullable=True)  # session_id or achievement_code
    description = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    user = db.relationship("User", back_populates="xp_transactions")

    def __repr__(self):
        return f"<XPTransaction user={self.user_id} +{self.amount}xp from {self.source_type}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "source_type": self.source_type,
            "reference_id": self.reference_id,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RewardTransaction(db.Model):
    """Ledger recording currency grants (coins/tokens)."""

    __tablename__ = "reward_transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    currency_type = db.Column(db.String(16), default="coins", nullable=False)
    source_type = db.Column(db.String(32), nullable=False, index=True)  # match, achievement, daily_login, daily_challenge
    reference_id = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    user = db.relationship("User", back_populates="reward_transactions")

    def __repr__(self):
        return f"<RewardTransaction user={self.user_id} +{self.amount} {self.currency_type}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "currency_type": self.currency_type,
            "source_type": self.source_type,
            "reference_id": self.reference_id,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
