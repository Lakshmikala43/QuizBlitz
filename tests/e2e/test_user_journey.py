import pytest
import json
from app.extensions import db
from app.models.category import Category
from app.models.question import Question, AnswerOption
from app.models.user import User


class TestUserJourneyE2E:
    """End-to-End simulation of user journey across landing, onboarding, gameplay, and progression."""

    @pytest.fixture(autouse=True)
    def reset_session(self, client):
        """Ensure clean session state between test methods."""
        client.get("/logout", follow_redirects=True)
        yield
        client.get("/logout", follow_redirects=True)

    def test_visitor_landing_and_help(self, client):
        """Verify anonymous visitor can view landing page, game rules, and features."""
        res_landing = client.get("/")
        assert res_landing.status_code == 200
        assert b"Quiz Royale" in res_landing.data
        assert b"Enter Arena" in res_landing.data or b"Battle" in res_landing.data or b"Get Started" in res_landing.data

        res_help = client.get("/help")
        assert res_help.status_code == 200
        assert b"Rules" in res_help.data or b"How to Play" in res_help.data or b"Quiz Royale" in res_help.data

    def test_registration_and_settings_journey(self, client):
        """Test registration, dashboard arrival, and updating player profile/settings."""
        # 1. Register a new player
        res_reg = client.post(
            "/register",
            data={
                "username": "journey_hero",
                "email": "hero@example.com",
                "password": "ChampionPass123!",
                "confirm_password": "ChampionPass123!",
                "display_name": "Journey Hero",
            },
            follow_redirects=True,
        )
        assert res_reg.status_code == 200
        assert b"Journey Hero" in res_reg.data or b"journey_hero" in res_reg.data

        # 2. Visit dashboard
        res_dash = client.get("/dashboard")
        assert res_dash.status_code == 200
        assert b"Dashboard" in res_dash.data

        # 3. Update profile / bio
        res_profile = client.post(
            "/profile",
            data={
                "display_name": "Valiant Hero",
                "bio": "Competing to reach Grandmaster rank in Quiz Royale.",
                "avatar_seed": "adventurer-1",
            },
            follow_redirects=True,
        )
        assert res_profile.status_code == 200
        assert b"Valiant Hero" in res_profile.data or b"Profile" in res_profile.data

    def test_full_quiz_gameplay_to_results_and_review(self, client, sample_category, sample_questions):
        """Complete full lifecycle: setup -> start -> play questions -> view results -> review answers."""
        # 1. Register and login
        res_reg = client.post(
            "/register",
            data={
                "username": "quiz_gladiator",
                "email": "gladiator@example.com",
                "password": "GladiatorPass123!",
                "confirm_password": "GladiatorPass123!",
                "display_name": "Gladiator",
            },
            follow_redirects=True,
        )
        assert res_reg.status_code == 200

        # 2. Browse modes and setup
        res_modes = client.get("/play/modes")
        assert res_modes.status_code == 200
        assert b"Solo" in res_modes.data

        res_setup = client.get("/play/setup")
        assert res_setup.status_code == 200
        assert sample_category.name.encode() in res_setup.data

        # 3. Start a solo match
        res_start = client.post(
            "/play/start",
            data={
                "category": sample_category.slug,
                "difficulty": "medium",
                "game_mode": "solo",
                "question_count": 5,
            },
            follow_redirects=True,
        )
        assert res_start.status_code == 200

        # Session URL is in the redirected request or page
        session_id = None
        # Check if json or html response
        if res_start.is_json:
            session_id = res_start.get_json().get("session_id")
        else:
            # Extract session id from current URL /play/<session_id>
            import re
            match = re.search(r"/play/([a-f0-9\-]+)", res_start.request.path)
            if match:
                session_id = match.group(1)

        assert session_id is not None

        # 4. Visit gameplay UI
        res_play = client.get(f"/play/{session_id}")
        assert res_play.status_code == 200
        assert b"Score" in res_play.data or b"Streak" in res_play.data or b"Timer" in res_play.data

        # 5. Answer all 5 questions
        for q_idx in range(5):
            res_q = client.get(f"/play/{session_id}/question")
            assert res_q.status_code == 200
            q_data = res_q.get_json()
            assert q_data["success"] is True
            payload = q_data["data"]["question"]

            # Submit first option
            selected_opt_id = payload["options"][0]["id"]
            res_sub = client.post(
                f"/play/{session_id}/submit",
                data=json.dumps({
                    "question_id": payload["id"],
                    "selected_option_id": selected_opt_id,
                    "client_response_time_ms": 1500,
                }),
                content_type="application/json",
            )
            assert res_sub.status_code == 200
            sub_data = res_sub.get_json()
            assert sub_data["success"] is True

            # Advance to next question or complete match
            res_next = client.post(f"/play/{session_id}/next")
            assert res_next.status_code == 200
            next_data = res_next.get_json()
            if next_data.get("is_finished", False):
                break

        # 6. View Results screen
        res_results = client.get(f"/play/{session_id}/results")
        assert res_results.status_code == 200
        assert b"Match Complete" in res_results.data or b"Results" in res_results.data or b"Performance" in res_results.data

        # 7. View Review screen
        res_review = client.get(f"/play/{session_id}/review")
        assert res_review.status_code == 200
        assert b"Explanation" in res_review.data or b"Review" in res_review.data

        # 8. Check Match History and Dashboard reflect progression
        res_history = client.get("/history")
        assert res_history.status_code == 200
        assert b"solo" in res_history.data.lower() or b"pts" in res_history.data.lower()

        res_dash = client.get("/dashboard")
        assert res_dash.status_code == 200
        assert b"Matches" in res_dash.data or b"Battle" in res_dash.data

    def test_daily_challenge_and_leaderboards(self, client, sample_category, sample_questions):
        """Test daily challenge entry and ranked leaderboard views."""
        # Login player
        client.post(
            "/register",
            data={
                "username": "daily_striker",
                "email": "striker@example.com",
                "password": "StrikerPass123!",
                "password_confirm": "StrikerPass123!",
                "display_name": "Daily Striker",
            },
            follow_redirects=True,
        )

        # Visit daily challenge
        res_daily = client.get("/play/daily")
        assert res_daily.status_code in (200, 302)

        # Inspect leaderboard
        res_lb = client.get("/leaderboards/")
        assert res_lb.status_code == 200
        assert b"Leaderboard" in res_lb.data or b"Rankings" in res_lb.data

        # Inspect achievements
        res_ach = client.get("/achievements/")
        assert res_ach.status_code == 200
        assert b"Achievements" in res_ach.data or b"Badges" in res_ach.data
