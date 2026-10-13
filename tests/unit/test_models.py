import pytest
from datetime import datetime, timezone, timedelta
from app.models.user import User
from app.models.category import Category
from app.models.question import Question, AnswerOption
from app.models.statistics import PlayerStatistics
from app.models.achievement import Achievement
from app.models.multiplayer import MultiplayerRoom, generate_room_code
from app.models.moderation import Report, AuditLog


class TestUserModel:
    """Unit test suite for User authentication and domain logic."""

    def test_password_hashing(self):
        user = User(username="cipher", email="cipher@royale.local")
        user.set_password("Secret123!")

        assert user.password_hash is not None
        assert user.password_hash != "Secret123!"
        assert user.check_password("Secret123!") is True
        assert user.check_password("WrongPassword") is False
        assert user.check_password("") is False

    def test_reset_token_generation_and_expiry(self):
        user = User(username="tokenuser", email="token@royale.local")
        token = user.generate_reset_token(expires_in_minutes=30)

        assert token is not None
        assert len(token) > 20
        assert user.verify_reset_token(token) is True
        assert user.verify_reset_token("invalid_token") is False

        # Test expiration
        user.reset_token_expiry = datetime.now(timezone.utc) - timedelta(minutes=5)
        assert user.verify_reset_token(token) is False

        # Clear token
        user.clear_reset_token()
        assert user.reset_token is None
        assert user.reset_token_expiry is None

    def test_user_roles(self):
        user = User(username="warrior", email="warrior@royale.local", is_admin=False)
        assert user.has_role("admin") is False

        admin_user = User(username="adminwarrior", email="admin@royale.local", is_admin=True)
        assert admin_user.has_role("admin") is True
        assert admin_user.has_role("player") is True


class TestCategoryAndQuestionModels:
    """Unit test suite for Category and anti-cheat Question models."""

    def test_category_properties(self):
        cat = Category(name="Mathematics", slug="math", is_active=True, sort_order=2)
        assert cat.name == "Mathematics"
        assert cat.slug == "math"
        d = cat.to_dict()
        assert d["name"] == "Mathematics"
        assert d["slug"] == "math"
        assert "question_count" in d

    def test_question_anti_cheat_serialization(self):
        q = Question(
            question_text="What is 2 + 2?",
            difficulty="easy",
            explanation="Basic arithmetic: 2 + 2 equals 4.",
            points=100,
            time_limit_sec=10,
            is_published=True,
        )
        opt1 = AnswerOption(option_text="3", is_correct=False, order_index=0)
        opt2 = AnswerOption(option_text="4", is_correct=True, order_index=1)
        q.options = [opt1, opt2]

        # Client dictionary MUST NOT contain correctness or explanation
        client_dict = q.to_client_dict(shuffle_options=False)
        assert "explanation" not in client_dict
        for opt in client_dict["options"]:
            assert "is_correct" not in opt

        # Admin dictionary MUST contain full fields
        admin_dict = q.to_admin_dict()
        assert admin_dict["explanation"] == "Basic arithmetic: 2 + 2 equals 4."
        assert any(opt["is_correct"] is True for opt in admin_dict["options"])


class TestPlayerStatisticsModel:
    """Unit test suite for progression, XP formulas, and percentages."""

    def test_level_calculation_curve(self):
        assert PlayerStatistics.calculate_level_from_xp(0) == 1
        assert PlayerStatistics.calculate_level_from_xp(100) >= 2
        assert PlayerStatistics.calculate_level_from_xp(1000) > PlayerStatistics.calculate_level_from_xp(100)

    def test_accuracy_and_win_rate_percentages(self):
        stats = PlayerStatistics(user_id=1)
        assert stats.accuracy_percentage == 0.0
        assert stats.win_rate_percentage == 0.0

        stats.total_answered = 20
        stats.total_correct = 15
        assert stats.accuracy_percentage == 75.0

        stats.total_matches = 10
        stats.wins = 6
        assert stats.win_rate_percentage == 60.0


class TestMultiplayerAndAuditModels:
    """Unit test suite for multiplayer room codes and audit logs."""

    def test_room_code_generation(self):
        code1 = generate_room_code(6)
        code2 = generate_room_code(6)
        assert len(code1) == 6
        assert len(code2) == 6
        assert code1.isalnum()
        # Ensure ambiguous chars excluded
        for char in "0O1I":
            assert char not in code1

    def test_audit_log_details_deserialization(self):
        log = AuditLog(
            action_type="delete_question",
            target_entity="question",
            target_id="42",
            details_json='{"reason": "duplicate", "actor": "admin"}',
        )
        details = log.get_details()
        assert details["reason"] == "duplicate"
        assert details["actor"] == "admin"
