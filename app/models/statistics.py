import math
from datetime import datetime, timezone, date
from app.extensions import db


class PlayerStatistics(db.Model):
    """Aggregate gameplay statistics and progression for a player."""

    __tablename__ = "player_statistics"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Progression
    total_xp = db.Column(db.Integer, default=0, nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    coins = db.Column(db.Integer, default=100, nullable=False)  # Starting bonus 100 coins

    # Performance
    total_matches = db.Column(db.Integer, default=0, nullable=False)
    wins = db.Column(db.Integer, default=0, nullable=False)
    total_correct = db.Column(db.Integer, default=0, nullable=False)
    total_answered = db.Column(db.Integer, default=0, nullable=False)
    highest_score = db.Column(db.Integer, default=0, nullable=False)
    highest_streak = db.Column(db.Integer, default=0, nullable=False)
    daily_streak = db.Column(db.Integer, default=0, nullable=False)
    last_active_date = db.Column(db.Date, nullable=True)

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = db.relationship("User", back_populates="statistics")

    def __repr__(self):
        return f"<PlayerStatistics user_id={self.user_id} lvl={self.level} xp={self.total_xp}>"

    @property
    def accuracy_percentage(self) -> float:
        if not self.total_answered or self.total_answered == 0:
            return 0.0
        total_correct = self.total_correct or 0
        return round((total_correct / self.total_answered) * 100.0, 1)

    @property
    def win_rate_percentage(self) -> float:
        if not self.total_matches or self.total_matches == 0:
            return 0.0
        wins = self.wins or 0
        return round((wins / self.total_matches) * 100.0, 1)


    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """Formula: XP = 100 * level^1.5 => level = floor((XP / 100) ^ (2/3)) + 1"""
        if xp <= 0:
            return 1
        lvl = int(math.floor((xp / 100.0) ** (2.0 / 3.0))) + 1
        return max(1, lvl)

    @staticmethod
    def xp_required_for_level(lvl: int) -> int:
        """Calculate total cumulative XP required to achieve level `lvl`."""
        if lvl <= 1:
            return 0
        return int(math.ceil(100.0 * ((lvl - 1) ** 1.5)))

    @property
    def xp_for_next_level(self) -> int:
        return self.xp_required_for_level(self.level + 1)

    @property
    def xp_progress_in_current_level(self) -> int:
        curr_lvl_req = self.xp_required_for_level(self.level)
        return max(0, self.total_xp - curr_lvl_req)

    @property
    def xp_needed_to_advance(self) -> int:
        next_lvl_req = self.xp_required_for_level(self.level + 1)
        curr_lvl_req = self.xp_required_for_level(self.level)
        return max(1, next_lvl_req - curr_lvl_req)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "total_xp": self.total_xp,
            "level": self.level,
            "coins": self.coins,
            "total_matches": self.total_matches,
            "wins": self.wins,
            "total_correct": self.total_correct,
            "total_answered": self.total_answered,
            "accuracy_percentage": self.accuracy_percentage,
            "win_rate_percentage": self.win_rate_percentage,
            "highest_score": self.highest_score,
            "highest_streak": self.highest_streak,
            "daily_streak": self.daily_streak,
            "xp_for_next_level": self.xp_for_next_level,
            "xp_progress_in_current_level": self.xp_progress_in_current_level,
            "xp_needed_to_advance": self.xp_needed_to_advance,
        }
