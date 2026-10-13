import pytest
import json
from app.extensions import db
from app.models.category import Category
from app.models.question import Question, AnswerOption
from app.models.user import User


class TestRestApiV1:
    """Comprehensive test suite for REST API v1 endpoints, anti-cheat scrubbing, and access controls."""

    @pytest.fixture(autouse=True)
    def reset_session(self, client):
        """Ensure clean session state between test methods."""
        client.get("/logout", follow_redirects=True)
        yield
        client.get("/logout", follow_redirects=True)

    def test_health_and_status(self, client):
        """Verify engine health liveness probe and telemetry status."""
        res_h = client.get("/api/v1/health")
        assert res_h.status_code == 200
        data_h = res_h.get_json()
        assert data_h["status"] == "success"
        assert data_h["data"]["status"] == "healthy"
        assert data_h["data"]["service"] == "Quiz Royale Gameplay Engine"

        res_s = client.get("/api/v1/status")
        assert res_s.status_code == 200
        data_s = res_s.get_json()
        assert data_s["status"] == "success"
        assert data_s["data"]["database"] == "connected"
        assert data_s["data"]["features"]["zero_external_api_keys"] is True

    def test_auth_workflow(self, client):
        """Test API registration, login, session inspection, and logout."""
        # Validation error with incomplete payload
        res_bad = client.post(
            "/api/v1/auth/register",
            data=json.dumps({"username": "api_newbie"}),
            content_type="application/json",
        )
        assert res_bad.status_code in (400, 422)

        # Successful registration
        res_reg = client.post(
            "/api/v1/auth/register",
            data=json.dumps({
                "username": "api_warrior",
                "email": "api_warrior@example.com",
                "password": "SecurePassword123!",
                "display_name": "API Warrior",
            }),
            content_type="application/json",
        )
        assert res_reg.status_code == 201
        data_reg = res_reg.get_json()
        assert data_reg["status"] == "success"
        assert data_reg["data"]["user"]["username"] == "api_warrior"

        # Check me endpoint (authenticated via login_user on register)
        res_me = client.get("/api/v1/auth/me")
        assert res_me.status_code == 200
        data_me = res_me.get_json()
        assert data_me["data"]["user"]["username"] == "api_warrior"

        # Logout
        res_logout = client.post("/api/v1/auth/logout")
        assert res_logout.status_code == 200

        # Me endpoint now unauthenticated
        res_me2 = client.get("/api/v1/auth/me")
        assert res_me2.status_code == 401

        # Re-login with valid credentials
        res_login = client.post(
            "/api/v1/auth/login",
            data=json.dumps({
                "login_identifier": "api_warrior",
                "password": "SecurePassword123!",
            }),
            content_type="application/json",
        )
        assert res_login.status_code == 200
        data_login = res_login.get_json()
        assert data_login["status"] == "success"
        assert data_login["data"]["user"]["username"] == "api_warrior"

    def test_categories_api(self, client, sample_category):
        """Verify categories catalog and single category endpoints."""
        res = client.get("/api/v1/categories")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        slugs = [c["slug"] for c in data["data"]]
        assert sample_category.slug in slugs

        # Single category details
        res_single = client.get(f"/api/v1/categories/{sample_category.slug}")
        assert res_single.status_code == 200
        data_single = res_single.get_json()
        assert data_single["data"]["name"] == sample_category.name

        # Non-existent category
        res_404 = client.get("/api/v1/categories/nonexistent-xyz")
        assert res_404.status_code == 404

    def test_sample_questions_anti_cheat(self, client, sample_category, sample_questions):
        """Ensure sample questions endpoint scrubs correct answers."""
        res = client.get(f"/api/v1/questions/sample?category={sample_category.slug}&limit=5")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        questions = data["data"]
        assert len(questions) > 0

        # Anti-cheat guarantee: correct_option_id and is_correct must NEVER be exposed
        for q in questions:
            assert "correct_option_id" not in q
            assert "correct_option" not in q
            for opt in q["options"]:
                assert "is_correct" not in opt

    def test_gameplay_session_api(self, client, test_user, sample_category, sample_questions):
        """Test authoritative game session creation, question retrieval, and answer submission."""
        # Login player
        client.post(
            "/login",
            data={"username_or_email": test_user.username, "password": "Password123!"},
            follow_redirects=True,
        )

        # Start game session
        res_start = client.post(
            "/api/v1/games/start",
            data=json.dumps({
                "category": sample_category.slug,
                "difficulty": "medium",
                "game_mode": "solo",
                "question_count": 5,
            }),
            content_type="application/json",
        )
        assert res_start.status_code in (200, 201)
        data_start = res_start.get_json()
        assert data_start["status"] == "success"
        session_id = data_start["data"]["id"]
        assert session_id is not None

        # Fetch current active question
        res_q = client.get(f"/api/v1/games/{session_id}/question")
        assert res_q.status_code == 200
        data_q = res_q.get_json()
        assert data_q["status"] == "success"
        q_payload = data_q["data"]["question"]
        assert "id" in q_payload
        assert len(q_payload["options"]) == 4

        # Submit answer
        first_opt_id = q_payload["options"][0]["id"]
        res_sub = client.post(
            f"/api/v1/games/{session_id}/submit",
            data=json.dumps({
                "question_id": q_payload["id"],
                "selected_option_id": first_opt_id,
                "client_response_time_ms": 1200,
            }),
            content_type="application/json",
        )
        assert res_sub.status_code == 200
        data_sub = res_sub.get_json()
        assert data_sub["status"] == "success"
        assert "is_correct" in data_sub["data"]
        assert "points_awarded" in data_sub["data"]

        # Session summary
        res_sum = client.get(f"/api/v1/games/{session_id}/summary")
        assert res_sum.status_code == 200
        data_sum = res_sum.get_json()
        assert data_sum["status"] == "success"
        assert "id" in data_sum["data"]

    def test_leaderboards_and_player_profiles(self, client, test_user):
        """Test leaderboards rankings and public player profile API."""
        res_lb = client.get("/api/v1/leaderboards")
        assert res_lb.status_code == 200
        data_lb = res_lb.get_json()
        assert data_lb["status"] == "success"
        assert "rankings" in data_lb["data"]

        # Player profile
        res_p = client.get(f"/api/v1/players/{test_user.username}")
        assert res_p.status_code == 200
        data_p = res_p.get_json()
        assert data_p["status"] == "success"
        assert data_p["data"]["username"] == test_user.username

        # Achievements
        res_ach = client.get("/api/v1/achievements")
        assert res_ach.status_code == 200
        data_ach = res_ach.get_json()
        assert data_ach["status"] == "success"
        assert isinstance(data_ach["data"], list)

    def test_multiplayer_room_api(self, client, test_user, sample_category):
        """Test multiplayer room creation, listing, and inspection via API."""
        client.post(
            "/login",
            data={"username_or_email": test_user.username, "password": "Password123!"},
            follow_redirects=True,
        )

        # Create room
        res_create = client.post(
            "/api/v1/multiplayer/rooms",
            data=json.dumps({
                "name": "API Tournament Arena",
                "category": sample_category.slug,
                "difficulty": "medium",
                "max_players": 4,
            }),
            content_type="application/json",
        )
        assert res_create.status_code == 201
        data_create = res_create.get_json()
        assert data_create["status"] == "success"
        room_code = data_create["data"]["room_code"]
        assert room_code is not None

        # Inspect room
        res_room = client.get(f"/api/v1/multiplayer/rooms/{room_code}")
        assert res_room.status_code == 200
        data_room = res_room.get_json()
        assert data_room["data"]["room_code"] == room_code

        # List rooms
        res_list = client.get("/api/v1/multiplayer/rooms")
        assert res_list.status_code == 200
        data_list = res_list.get_json()
        codes = [r["room_code"] for r in data_list["data"]]
        assert room_code in codes

    def test_admin_api_rbac(self, client, test_user, test_admin):
        """Verify strict role-based access control protecting administrative API endpoints."""
        # Unauthenticated access -> 401
        res_anon = client.get("/api/v1/admin/overview")
        assert res_anon.status_code in (401, 403)

        # Regular player access -> 403 Forbidden
        client.post(
            "/login",
            data={"username_or_email": test_user.username, "password": "Password123!"},
            follow_redirects=True,
        )
        res_forbidden = client.get("/api/v1/admin/overview")
        assert res_forbidden.status_code == 403

        # Logout regular player
        client.get("/logout", follow_redirects=True)

        # Admin access -> 200 OK
        client.post(
            "/login",
            data={"username_or_email": test_admin.username, "password": "AdminPass123!"},
            follow_redirects=True,
        )
        res_admin = client.get("/api/v1/admin/overview")
        assert res_admin.status_code == 200
        data_admin = res_admin.get_json()
        assert data_admin["status"] == "success"
        assert "metrics" in data_admin["data"]

        # Admin users search
        res_users = client.get("/api/v1/admin/users")
        assert res_users.status_code == 200

        # Admin audit logs
        res_logs = client.get("/api/v1/admin/audit-logs")
        assert res_logs.status_code == 200
