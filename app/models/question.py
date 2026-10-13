import random
from datetime import datetime, timezone
from app.extensions import db


class Question(db.Model):
    """Quiz question entity."""

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(16), default="medium", nullable=False, index=True)  # 'easy', 'medium', 'hard'
    explanation = db.Column(db.Text, nullable=True)
    time_limit_sec = db.Column(db.Integer, default=15, nullable=False)
    points = db.Column(db.Integer, default=100, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False, index=True)
    image_url = db.Column(db.String(255), nullable=True)

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
    category = db.relationship("Category", back_populates="questions")
    options = db.relationship("AnswerOption", back_populates="question", cascade="all, delete-orphan", order_by="AnswerOption.order_index")
    session_questions = db.relationship("SessionQuestion", back_populates="question", cascade="all, delete-orphan")
    submissions = db.relationship("AnswerSubmission", back_populates="question")
    reports = db.relationship("Report", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question #{self.id} [{self.difficulty}] {self.question_text[:30]}...>"

    @property
    def correct_option(self):
        """Retrieve the correct answer option on the server."""
        for opt in self.options:
            if opt.is_correct:
                return opt
        return None

    def to_client_dict(self, shuffle_options: bool = True) -> dict:
        """
        Serialize question for player client.
        CRITICAL: Never includes is_correct flag or explanation before submission!
        """
        opts = [opt.to_client_dict() for opt in self.options]
        if shuffle_options:
            random.shuffle(opts)
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "question_text": self.question_text,
            "difficulty": self.difficulty,
            "time_limit_sec": self.time_limit_sec,
            "points": self.points,
            "image_url": self.image_url,
            "options": opts,
        }

    def to_admin_dict(self) -> dict:
        """Full serialization including answers and explanation for admin."""
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "question_text": self.question_text,
            "difficulty": self.difficulty,
            "explanation": self.explanation,
            "time_limit_sec": self.time_limit_sec,
            "points": self.points,
            "is_published": self.is_published,
            "image_url": self.image_url,
            "options": [opt.to_admin_dict() for opt in self.options],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AnswerOption(db.Model):
    """Answer choice for a quiz question."""

    __tablename__ = "answer_options"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)

    # Relationships
    question = db.relationship("Question", back_populates="options")
    submissions = db.relationship("AnswerSubmission", back_populates="selected_option")

    def __repr__(self):
        return f"<AnswerOption #{self.id} for Q#{self.question_id} (correct={self.is_correct})>"

    def to_client_dict(self) -> dict:
        """Safe client serialization hiding the correctness key."""
        return {
            "id": self.id,
            "option_text": self.option_text,
        }

    def to_admin_dict(self) -> dict:
        """Full representation including answer correctness."""
        return {
            "id": self.id,
            "option_text": self.option_text,
            "is_correct": self.is_correct,
            "order_index": self.order_index,
        }
