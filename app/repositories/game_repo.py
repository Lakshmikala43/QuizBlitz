from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlalchemy import desc
from app.extensions import db
from app.models.session import (
    QuizSession,
    SessionQuestion,
    AnswerSubmission,
    MatchResult,
)
from app.repositories.base import BaseRepository


class GameRepository(BaseRepository[QuizSession]):
    """Data-access repository for game sessions, submissions, and match outcomes."""

    def __init__(self):
        super().__init__(QuizSession)

    def create_game_session(
        self,
        user_id: int,
        category_id: Optional[int],
        game_mode: str,
        difficulty: str,
        total_questions: int,
        time_limit_sec: Optional[int] = None,
    ) -> QuizSession:
        """Create and persist a new authoritative game session."""
        session = QuizSession(
            user_id=user_id,
            category_id=category_id,
            game_mode=game_mode,
            difficulty=difficulty,
            total_questions=total_questions,
            time_remaining_sec=time_limit_sec,
            lives_remaining=3 if game_mode == "survival" else 0,
            status="in_progress",
        )
        db.session.add(session)
        db.session.commit()
        return session

    def attach_questions_to_session(self, session_id: str, question_ids: List[int]) -> None:
        """Map assigned questions in strict order to the session."""
        for idx, qid in enumerate(question_ids):
            sq = SessionQuestion(
                session_id=session_id,
                question_id=qid,
                question_order=idx,
            )
            db.session.add(sq)
        db.session.commit()

    def get_session_question_by_order(
        self, session_id: str, order_index: int
    ) -> Optional[SessionQuestion]:
        """Fetch the specific question assigned to an index order."""
        return (
            db.session.query(SessionQuestion)
            .filter_by(session_id=session_id, question_order=order_index)
            .first()
        )

    def record_submission(
        self,
        session_id: str,
        question_id: int,
        selected_option_id: Optional[int],
        is_correct: bool,
        response_time_ms: int,
        points_awarded: int,
        streak_bonus: int,
        speed_bonus: int,
        idempotency_key: Optional[str] = None,
    ) -> AnswerSubmission:
        """Persist an answer submission."""
        submission = AnswerSubmission(
            session_id=session_id,
            question_id=question_id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
            points_awarded=points_awarded,
            streak_bonus=streak_bonus,
            speed_bonus=speed_bonus,
            idempotency_key=idempotency_key,
        )
        db.session.add(submission)
        db.session.commit()
        return submission

    def get_submission_by_idempotency_key(
        self, session_id: str, idempotency_key: str
    ) -> Optional[AnswerSubmission]:
        """Check for existing submission with the idempotency key."""
        return (
            db.session.query(AnswerSubmission)
            .filter_by(session_id=session_id, idempotency_key=idempotency_key)
            .first()
        )

    def finalize_match_result(
        self,
        session: QuizSession,
        xp_earned: int,
        coins_earned: int,
    ) -> MatchResult:
        """Calculate and store final match outcome metrics."""
        submissions = session.submissions
        correct_count = sum(1 for s in submissions if s.is_correct)
        total_q = session.total_questions
        accuracy = (correct_count / total_q * 100.0) if total_q > 0 else 0.0
        total_time = sum(s.response_time_ms for s in submissions)

        result = MatchResult(
            session_id=session.id,
            user_id=session.user_id,
            game_mode=session.game_mode,
            total_score=session.current_score,
            correct_answers=correct_count,
            total_questions=total_q,
            accuracy_pct=accuracy,
            best_streak=session.best_streak,
            total_time_ms=total_time,
            xp_earned=xp_earned,
            coins_earned=coins_earned,
        )
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)

        db.session.add(result)
        db.session.commit()
        return result

    def get_user_match_history(
        self, user_id: int, page: int = 1, per_page: int = 10
    ):
        """Fetch paginated match history for a specific player."""
        query = (
            db.session.query(MatchResult)
            .filter_by(user_id=user_id)
            .order_by(MatchResult.recorded_at.desc())
        )
        return self.paginate(query, page=page, per_page=per_page)

    def get_recent_global_matches(self, limit: int = 10) -> List[MatchResult]:
        """Fetch recent completed matches across all players for the live activity feed."""
        return (
            db.session.query(MatchResult)
            .order_by(MatchResult.recorded_at.desc())
            .limit(limit)
            .all()
        )
