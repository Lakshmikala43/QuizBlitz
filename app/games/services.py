from datetime import datetime, timezone
from typing import Optional, Tuple, Dict
from app.extensions import db
from app.models.session import QuizSession, SessionQuestion, AnswerSubmission
from app.models.question import Question, AnswerOption
from app.models.category import Category
from app.repositories import GameRepository, QuestionRepository, StatsRepository, CategoryRepository
from app.games.scoring import ScoringEngine

game_repo = GameRepository()
question_repo = QuestionRepository()
stats_repo = StatsRepository()
category_repo = CategoryRepository()


class QuizSessionService:
    """Manages authoritative quiz lifecycle, state transitions, and answer submissions."""

    @staticmethod
    def start_session(
        user_id: int,
        category_slug: Optional[str] = None,
        difficulty: str = "mixed",
        question_count: int = 10,
        game_mode: str = "solo",
    ) -> Tuple[bool, str, Optional[QuizSession]]:
        """Validate configuration, select randomized question pool, and initialize session."""
        category = None
        category_id = None
        if category_slug and category_slug != "all":
            category = category_repo.get_by_slug(category_slug)
            if not category or not category.is_active:
                return False, "Selected category is not available.", None
            category_id = category.id

        # Clamp question count
        count = max(5, min(25, question_count))

        # Query randomized questions pool
        pool = question_repo.get_random_questions(
            category_id=category_id,
            difficulty=difficulty,
            count=count,
        )

        if not pool:
            return False, "No questions currently available for this selection.", None

        # Create session
        session = game_repo.create_game_session(
            user_id=user_id,
            category_id=category_id,
            game_mode=game_mode,
            difficulty=difficulty,
            total_questions=len(pool),
            time_limit_sec=60 if game_mode == "time_attack" else None,
        )

        # Attach ordered questions
        game_repo.attach_questions_to_session(session.id, [q.id for q in pool])

        return True, "Session initialized successfully.", session

    @staticmethod
    def get_current_question_payload(session_id: str, user_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Fetch the current question for the player.
        Conceals correct answers and records authoritative display timestamp.
        """
        session = game_repo.get_by_id(session_id)
        if not session:
            return False, "Session not found.", None

        if session.user_id != user_id:
            return False, "Unauthorized access to session.", None

        if session.status != "in_progress":
            return False, f"Session is {session.status}.", None

        # Check if completed by question index
        if session.current_question_index >= session.total_questions:
            return False, "All questions have been answered.", None

        # Retrieve mapped session question
        sq = game_repo.get_session_question_by_order(session.id, session.current_question_index)
        if not sq or not sq.question:
            return False, "Failed to load session question.", None

        # Record start timestamp if first viewed
        now = datetime.now(timezone.utc)
        if not sq.displayed_at:
            sq.displayed_at = now
            db.session.commit()

        # Build safe client dictionary (never includes is_correct!)
        q = sq.question
        q_client = q.to_client_dict(shuffle_options=True)

        return True, "Question loaded.", {
            "session_id": session.id,
            "game_mode": session.game_mode,
            "current_index": session.current_question_index + 1,
            "total_questions": session.total_questions,
            "current_score": session.current_score,
            "current_streak": session.current_streak,
            "lives_remaining": session.lives_remaining,
            "question": q_client,
            "started_at": sq.displayed_at.isoformat(),
        }

    @staticmethod
    def submit_answer(
        session_id: str,
        user_id: int,
        question_id: int,
        selected_option_id: Optional[int],
        idempotency_key: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authoritatively validate answer, verify elapsed time, compute scores,
        and update session state.
        """
        session = game_repo.get_by_id(session_id)
        if not session or session.status != "in_progress":
            return False, "Game session is inactive or completed.", None

        if session.user_id != user_id:
            return False, "Unauthorized.", None

        # Idempotency check: if already submitted, return previous result
        if idempotency_key:
            existing = game_repo.get_submission_by_idempotency_key(session_id, idempotency_key)
            if existing:
                return True, "Duplicate submission acknowledged.", {
                    "is_correct": existing.is_correct,
                    "points_awarded": existing.points_awarded,
                    "current_score": session.current_score,
                    "current_streak": session.current_streak,
                }

        # Current question check
        sq = game_repo.get_session_question_by_order(session.id, session.current_question_index)
        if not sq or sq.question_id != question_id:
            return False, "Invalid or out-of-order question submission.", None

        # Calculate authoritative server response time
        now = datetime.now(timezone.utc)
        start_time = sq.displayed_at or session.started_at
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        elapsed_ms = int((now - start_time).total_seconds() * 1000)

        # Retrieve question and evaluate correctness
        question = sq.question
        is_correct = False
        correct_option_id = question.correct_option.id if question.correct_option else None

        if selected_option_id is not None:
            chosen_opt = db.session.get(AnswerOption, selected_option_id)
            if chosen_opt and chosen_opt.question_id == question.id and chosen_opt.is_correct:
                is_correct = True

        # Calculate authoritative score
        points, streak_pts, speed_pts, new_streak = ScoringEngine.calculate_submission_score(
            difficulty=question.difficulty,
            is_correct=is_correct,
            response_time_ms=elapsed_ms,
            time_limit_sec=question.time_limit_sec,
            current_streak=session.current_streak,
        )

        # Update session metrics
        session.current_score += points
        session.current_streak = new_streak
        if session.current_streak > session.best_streak:
            session.best_streak = session.current_streak

        # Survival Mode Life Depletion Check
        game_over = False
        if session.game_mode == "survival" and not is_correct:
            session.lives_remaining -= 1
            if session.lives_remaining <= 0:
                game_over = True

        # Persist submission record
        game_repo.record_submission(
            session_id=session.id,
            question_id=question.id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            response_time_ms=elapsed_ms,
            points_awarded=points,
            streak_bonus=streak_pts,
            speed_bonus=speed_pts,
            idempotency_key=idempotency_key,
        )

        db.session.commit()

        return True, "Answer evaluated.", {
            "is_correct": is_correct,
            "correct_option_id": correct_option_id,
            "explanation": question.explanation,
            "points_awarded": points,
            "speed_bonus": speed_pts,
            "streak_bonus": streak_pts,
            "current_score": session.current_score,
            "current_streak": session.current_streak,
            "lives_remaining": session.lives_remaining,
            "game_over": game_over,
        }

    @staticmethod
    def advance_session(session_id: str, user_id: int) -> Tuple[bool, bool]:
        """
        Advance current question pointer.
        Returns: (success, is_finished)
        """
        session = game_repo.get_by_id(session_id)
        if not session or session.user_id != user_id:
            return False, False

        session.current_question_index += 1

        is_finished = (
            session.current_question_index >= session.total_questions
            or (session.game_mode == "survival" and session.lives_remaining <= 0)
        )

        if is_finished:
            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)

            # Compute match outcome
            submissions = session.submissions
            correct_count = sum(1 for s in submissions if s.is_correct)
            total_q = len(submissions) or 1
            acc_pct = (correct_count / total_q) * 100.0

            xp, coins = ScoringEngine.calculate_match_rewards(
                total_score=session.current_score,
                accuracy_pct=acc_pct,
                game_mode=session.game_mode,
                best_streak=session.best_streak,
            )

            # Persist finalized match result
            game_repo.finalize_match_result(session, xp_earned=xp, coins_earned=coins)

            # Update player stats & achievements
            stats_repo.apply_match_rewards(
                user_id=user_id,
                xp=xp,
                coins=coins,
                score=session.current_score,
                streak=session.best_streak,
                correct_count=correct_count,
                total_count=total_q,
                is_win=acc_pct >= 70.0,
                session_id=session.id,
            )

        db.session.commit()
        return True, is_finished
