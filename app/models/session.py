import uuid
from datetime import datetime, timezone
from app.extensions import db


class QuizSession(db.Model):
    """Authoritative game session."""

    __tablename__ = "quiz_sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    game_mode = db.Column(db.String(24), default="solo", nullable=False, index=True)  # solo, time_attack, survival, daily, practice, multiplayer
    difficulty = db.Column(db.String(16), default="mixed", nullable=False)  # easy, medium, hard, mixed
    total_questions = db.Column(db.Integer, default=10, nullable=False)
    current_question_index = db.Column(db.Integer, default=0, nullable=False)
    current_score = db.Column(db.Integer, default=0, nullable=False)
    current_streak = db.Column(db.Integer, default=0, nullable=False)
    best_streak = db.Column(db.Integer, default=0, nullable=False)
    lives_remaining = db.Column(db.Integer, default=3, nullable=False)  # Used in Survival mode
    time_remaining_sec = db.Column(db.Integer, nullable=True)  # Used in Time Attack
    status = db.Column(db.String(24), default="in_progress", nullable=False, index=True)  # created, in_progress, completed, abandoned, expired

    started_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="quiz_sessions")
    category = db.relationship("Category", back_populates="quiz_sessions")
    session_questions = db.relationship("SessionQuestion", back_populates="session", cascade="all, delete-orphan", order_by="SessionQuestion.question_order")
    submissions = db.relationship("AnswerSubmission", back_populates="session", cascade="all, delete-orphan", order_by="AnswerSubmission.submitted_at")
    match_result = db.relationship("MatchResult", back_populates="session", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizSession {self.id[:8]} user={self.user_id} mode={self.game_mode} status={self.status}>"

    @property
    def is_finished(self) -> bool:
        return self.status in ("completed", "abandoned", "expired")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "All Categories",
            "game_mode": self.game_mode,
            "difficulty": self.difficulty,
            "total_questions": self.total_questions,
            "current_question_index": self.current_question_index,
            "current_score": self.current_score,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "lives_remaining": self.lives_remaining,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class SessionQuestion(db.Model):
    """Ordered mapping of questions assigned to a specific quiz session."""

    __tablename__ = "session_questions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_order = db.Column(db.Integer, default=0, nullable=False)
    displayed_at = db.Column(db.DateTime, nullable=True)

    session = db.relationship("QuizSession", back_populates="session_questions")
    question = db.relationship("Question", back_populates="session_questions")

    __table_args__ = (
        db.UniqueConstraint("session_id", "question_order", name="uq_session_order"),
    )

    def __repr__(self):
        return f"<SessionQuestion session={self.session_id[:8]} order={self.question_order} qid={self.question_id}>"


class AnswerSubmission(db.Model):
    """Record of a player's answer to an individual question."""

    __tablename__ = "answer_submissions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_option_id = db.Column(db.Integer, db.ForeignKey("answer_options.id", ondelete="SET NULL"), nullable=True)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    response_time_ms = db.Column(db.Integer, default=0, nullable=False)
    points_awarded = db.Column(db.Integer, default=0, nullable=False)
    streak_bonus = db.Column(db.Integer, default=0, nullable=False)
    speed_bonus = db.Column(db.Integer, default=0, nullable=False)
    idempotency_key = db.Column(db.String(64), nullable=True, index=True)

    submitted_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    session = db.relationship("QuizSession", back_populates="submissions")
    question = db.relationship("Question", back_populates="submissions")
    selected_option = db.relationship("AnswerOption", back_populates="submissions")

    def __repr__(self):
        return f"<AnswerSubmission session={self.session_id[:8]} qid={self.question_id} correct={self.is_correct} pts={self.points_awarded}>"

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question_id": self.question_id,
            "selected_option_id": self.selected_option_id,
            "is_correct": self.is_correct,
            "response_time_ms": self.response_time_ms,
            "points_awarded": self.points_awarded,
            "streak_bonus": self.streak_bonus,
            "speed_bonus": self.speed_bonus,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }


class MatchResult(db.Model):
    """Permanent finalized match record for ranking and analytics."""

    __tablename__ = "match_results"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("quiz_sessions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game_mode = db.Column(db.String(24), nullable=False, index=True)
    total_score = db.Column(db.Integer, default=0, nullable=False, index=True)
    correct_answers = db.Column(db.Integer, default=0, nullable=False)
    total_questions = db.Column(db.Integer, default=0, nullable=False)
    accuracy_pct = db.Column(db.Float, default=0.0, nullable=False)
    best_streak = db.Column(db.Integer, default=0, nullable=False)
    total_time_ms = db.Column(db.Integer, default=0, nullable=False)
    xp_earned = db.Column(db.Integer, default=0, nullable=False)
    coins_earned = db.Column(db.Integer, default=0, nullable=False)

    recorded_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    session = db.relationship("QuizSession", back_populates="match_result")
    user = db.relationship("User", back_populates="match_results")

    def __repr__(self):
        return f"<MatchResult user={self.user_id} mode={self.game_mode} score={self.total_score}>"

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "game_mode": self.game_mode,
            "total_score": self.total_score,
            "correct_answers": self.correct_answers,
            "total_questions": self.total_questions,
            "accuracy_pct": round(self.accuracy_pct, 1),
            "best_streak": self.best_streak,
            "total_time_ms": self.total_time_ms,
            "xp_earned": self.xp_earned,
            "coins_earned": self.coins_earned,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }
