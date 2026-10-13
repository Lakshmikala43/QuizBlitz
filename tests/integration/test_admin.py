import pytest
from app.extensions import db
from app.models.category import Category
from app.models.question import Question
from app.models.user import User
from app.models.moderation import Report, AuditLog


class TestAdminIntegration:
    """Integration test suite for administrative management, security guards, and audit trail."""

    @pytest.fixture(autouse=True)
    def reset_session(self, client):
        """Ensure pristine session state before and after each test."""
        client.get("/logout", follow_redirects=True)
        yield
        client.get("/logout", follow_redirects=True)

    def test_admin_route_unauthorized_access(self, client, test_user):
        # Unauthenticated access -> redirects to login
        res_anon = client.get("/admin/", follow_redirects=False)
        assert res_anon.status_code in (302, 401, 403)

        # Authenticated as regular player -> 403 Forbidden
        client.post(
            "/login",
            data={"username_or_email": test_user.username, "password": "Password123!"},
            follow_redirects=True,
        )
        res_player = client.get("/admin/", follow_redirects=False)
        assert res_player.status_code == 403

    def test_admin_dashboard_metrics(self, client, test_admin, sample_category, sample_questions):
        client.post(
            "/login",
            data={"username_or_email": test_admin.username, "password": "AdminPass123!"},
            follow_redirects=True,
        )
        res = client.get("/admin/")

        assert res.status_code == 200
        assert b"Overview & Diagnostics" in res.data
        assert b"Registered Warriors" in res.data

    def test_admin_category_management(self, client, test_admin, app):
        client.post(
            "/login",
            data={"username_or_email": test_admin.username, "password": "AdminPass123!"},
            follow_redirects=True,
        )

        # Create category
        res = client.post(
            "/admin/categories/create",
            data={
                "name": "Artificial Intelligence",
                "slug": "ai",
                "description": "Machine learning, neural networks, and LLMs.",
                "color_hex": "#8b5cf6",
                "sort_order": 99,
            },
            follow_redirects=True,
        )
        assert res.status_code == 200

        with app.app_context():
            cat = Category.query.filter_by(slug="ai").first()
            assert cat is not None
            assert cat.name == "Artificial Intelligence"

            # Check audit log was written
            log = AuditLog.query.filter_by(action_type="create_category", target_id=str(cat.id)).first()
            assert log is not None

    def test_admin_question_management(self, client, test_admin, sample_category, app):
        client.post(
            "/login",
            data={"username_or_email": test_admin.username, "password": "AdminPass123!"},
            follow_redirects=True,
        )

        res = client.post(
            "/admin/questions/create",
            data={
                "category_id": sample_category.id,
                "question_text": "What is Python's Global Interpreter Lock called?",
                "difficulty": "medium",
                "points": 100,
                "time_limit_sec": 15,
                "explanation": "GIL stands for Global Interpreter Lock.",
                "option_0": "GIL",
                "option_1": "JIT",
                "option_2": "V8",
                "option_3": "JVM",
                "correct_option": "0",
                "is_published": "1",
            },
            follow_redirects=True,
        )
        assert res.status_code == 200

        with app.app_context():
            q = Question.query.filter(Question.question_text.like("%Global Interpreter Lock%")).first()
            assert q is not None
            assert len(q.options) == 4
            assert q.correct_option.option_text == "GIL"

    def test_admin_user_status_toggle(self, client, test_admin, test_user, app):
        client.post(
            "/login",
            data={"username_or_email": test_admin.username, "password": "AdminPass123!"},
            follow_redirects=True,
        )

        # Suspend user
        res = client.post(f"/admin/users/{test_user.id}/toggle-status", follow_redirects=True)
        assert res.status_code == 200

        with app.app_context():
            u = db.session.get(User, test_user.id)
            assert u.is_active is False

        # Reactivate user
        res2 = client.post(f"/admin/users/{test_user.id}/toggle-status", follow_redirects=True)
        assert res2.status_code == 200

        with app.app_context():
            u = db.session.get(User, test_user.id)
            assert u.is_active is True

    def test_admin_report_resolution(self, client, test_admin, test_user, sample_questions, app):
        client.post(
            "/login",
            data={"username_or_email": test_admin.username, "password": "AdminPass123!"},
            follow_redirects=True,
        )

        with app.app_context():
            q = sample_questions[0]
            report = Report(
                question_id=q.id,
                reporter_user_id=test_user.id,
                reason="typo",
                details="Minor typo in question description.",
                status="pending",
            )
            db.session.add(report)
            db.session.commit()
            report_id = report.id

        # Resolve report and unpublish question
        res = client.post(
            f"/admin/reports/{report_id}/resolve",
            data={
                "admin_notes": "Reviewed and unpublished for editorial correction.",
                "unpublish_question": "1",
            },
            follow_redirects=True,
        )
        assert res.status_code == 200

        with app.app_context():
            r = db.session.get(Report, report_id)
            assert r.status == "resolved"
            assert r.question.is_published is False
