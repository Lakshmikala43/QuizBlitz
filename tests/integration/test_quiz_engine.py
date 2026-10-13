import pytest
from app.extensions import db
from app.games.services import QuizSessionService
from app.models.session import QuizSession, MatchResult
from app.models.question import Question, AnswerOption
from app.models.statistics import PlayerStatistics


class TestQuizEngineIntegration:
    """Integration test suite for authoritative quiz gameplay lifecycle."""

    def test_start_session(self, app, test_user, sample_category, sample_questions):
        with app.app_context():
            success, msg, session = QuizSessionService.start_session(
                user_id=test_user.id,
                category_slug=sample_category.slug,
                difficulty="medium",
                question_count=5,
                game_mode="solo",
            )
            assert success is True
            assert session is not None
            assert session.status == "in_progress"
            assert session.total_questions == 5
            assert session.current_score == 0
            assert len(session.session_questions) == 5

    def test_anti_cheat_current_question_payload(self, app, test_user, sample_category, sample_questions):
        with app.app_context():
            _, _, session = QuizSessionService.start_session(
                user_id=test_user.id,
                category_slug=sample_category.slug,
                question_count=5,
            )

            success, msg, payload = QuizSessionService.get_current_question_payload(
                session_id=session.id,
                user_id=test_user.id,
            )
            assert success is True
            assert payload["session_id"] == session.id
            assert payload["current_index"] == 1
            assert "question" in payload

            q_data = payload["question"]
            assert "explanation" not in q_data
            for opt in q_data["options"]:
                assert "is_correct" not in opt

    def test_authoritative_answer_submission(self, app, test_user, sample_category, sample_questions):
        with app.app_context():
            _, _, session = QuizSessionService.start_session(
                user_id=test_user.id,
                category_slug=sample_category.slug,
                question_count=5,
            )

            # Fetch first question
            sq = session.session_questions[0]
            q = sq.question
            correct_opt = [o for o in q.options if o.is_correct][0]

            # Submit correct answer
            success, msg, result = QuizSessionService.submit_answer(
                session_id=session.id,
                user_id=test_user.id,
                question_id=q.id,
                selected_option_id=correct_opt.id,
                idempotency_key="unique-sub-1",
            )

            assert success is True
            assert result["is_correct"] is True
            assert result["points_awarded"] > 0
            assert result["current_streak"] == 1

            # Advance to next question
            adv_success, is_finished = QuizSessionService.advance_session(session.id, test_user.id)
            assert adv_success is True

            # Refresh session
            s_refreshed = db.session.get(QuizSession, session.id)
            assert s_refreshed.current_score > 0
            assert s_refreshed.current_question_index == 1


    def test_idempotent_duplicate_submission(self, app, test_user, sample_category, sample_questions):
        with app.app_context():
            _, _, session = QuizSessionService.start_session(
                user_id=test_user.id,
                category_slug=sample_category.slug,
                question_count=5,
            )

            sq = session.session_questions[0]
            correct_opt = [o for o in sq.question.options if o.is_correct][0]

            # First submission
            s1, _, res1 = QuizSessionService.submit_answer(
                session_id=session.id,
                user_id=test_user.id,
                question_id=sq.question_id,
                selected_option_id=correct_opt.id,
                idempotency_key="idempotent-key-42",
            )
            score_after_first = res1["current_score"]

            # Duplicate submission with same key
            s2, msg2, res2 = QuizSessionService.submit_answer(
                session_id=session.id,
                user_id=test_user.id,
                question_id=sq.question_id,
                selected_option_id=correct_opt.id,
                idempotency_key="idempotent-key-42",
            )
            assert s2 is True
            assert "Duplicate" in msg2 or res2["current_score"] == score_after_first

    def test_survival_mode_lives_decrement(self, app, test_user, sample_category, sample_questions):
        with app.app_context():
            _, _, session = QuizSessionService.start_session(
                user_id=test_user.id,
                category_slug=sample_category.slug,
                question_count=5,
                game_mode="survival",
            )
            assert session.lives_remaining == 3

            sq = session.session_questions[0]
            wrong_opt = [o for o in sq.question.options if not o.is_correct][0]

            # Submit wrong answer
            success, msg, result = QuizSessionService.submit_answer(
                session_id=session.id,
                user_id=test_user.id,
                question_id=sq.question_id,
                selected_option_id=wrong_opt.id,
            )
            assert success is True
            assert result["is_correct"] is False
            assert result["lives_remaining"] == 2
