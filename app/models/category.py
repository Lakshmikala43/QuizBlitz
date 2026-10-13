from datetime import datetime, timezone
from app.extensions import db


class Category(db.Model):
    """Quiz topic category."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(64), default="terminal", nullable=False)
    color_hex = db.Column(db.String(16), default="#6366f1", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    questions = db.relationship("Question", back_populates="category", cascade="all, delete-orphan")
    quiz_sessions = db.relationship("QuizSession", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name} ({self.slug})>"

    @property
    def question_count(self) -> int:
        return len([q for q in self.questions if q.is_published])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "icon": self.icon,
            "color_hex": self.color_hex,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "question_count": self.question_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
