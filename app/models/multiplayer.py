import random
import string
from datetime import datetime, timezone
from app.extensions import db


def generate_room_code(length: int = 6) -> str:
    """Generate a random alphanumeric room code."""
    chars = string.ascii_uppercase + string.digits
    # Avoid ambiguous characters like 0/O, 1/I
    chars = chars.replace("0", "").replace("O", "").replace("1", "").replace("I", "")
    return "".join(random.choice(chars) for _ in range(length))


class MultiplayerRoom(db.Model):
    """Real-time multiplayer match room."""

    __tablename__ = "multiplayer_rooms"

    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), unique=True, nullable=False, index=True, default=generate_room_code)
    host_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    difficulty = db.Column(db.String(16), default="medium", nullable=False)
    question_count = db.Column(db.Integer, default=10, nullable=False)
    max_players = db.Column(db.Integer, default=8, nullable=False)
    status = db.Column(db.String(24), default="waiting", nullable=False, index=True)  # waiting, starting, in_progress, finished, closed
    current_question_index = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    finished_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    host = db.relationship("User", foreign_keys=[host_user_id])
    category = db.relationship("Category")
    participants = db.relationship("RoomParticipant", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MultiplayerRoom {self.room_code} (host={self.host_user_id}, status={self.status})>"

    @property
    def participant_count(self) -> int:
        return len(self.participants)

    def to_dict(self):
        return {
            "id": self.id,
            "room_code": self.room_code,
            "host_user_id": self.host_user_id,
            "host_username": self.host.username if self.host else "Unknown",
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "All Categories",
            "difficulty": self.difficulty,
            "question_count": self.question_count,
            "max_players": self.max_players,
            "participant_count": self.participant_count,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "participants": [p.to_dict() for p in self.participants],
        }


class RoomParticipant(db.Model):
    """Participant in a multiplayer room."""

    __tablename__ = "room_participants"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("multiplayer_rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_ready = db.Column(db.Boolean, default=False, nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    current_streak = db.Column(db.Integer, default=0, nullable=False)
    is_connected = db.Column(db.Boolean, default=True, nullable=False)
    joined_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    room = db.relationship("MultiplayerRoom", back_populates="participants")
    user = db.relationship("User", back_populates="room_participations")

    __table_args__ = (
        db.UniqueConstraint("room_id", "user_id", name="uq_room_user"),
    )

    def __repr__(self):
        return f"<RoomParticipant room_id={self.room_id} user_id={self.user_id} score={self.score}>"

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "Unknown",
            "display_name": self.user.effective_display_name if self.user else "Unknown",
            "avatar_seed": self.user.avatar_seed if self.user else "default",
            "is_ready": self.is_ready,
            "score": self.score,
            "current_streak": self.current_streak,
            "is_connected": self.is_connected,
        }
