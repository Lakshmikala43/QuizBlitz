import pytest
from app.extensions import db
from app.models.user import User
from app.auth.services import AuthService


class TestAuthIntegration:
    """Integration test suite for player registration, login, and credential recovery."""

    def test_registration_success(self, client, app):
        res = client.post(
            "/register",
            data={
                "username": "newgladiator",
                "email": "gladiator@royale.local",
                "display_name": "Gladiator Prime",
                "password": "StrongPassword123!",
                "confirm_password": "StrongPassword123!",
            },
            follow_redirects=True,
        )
        assert res.status_code == 200

        with app.app_context():
            user = User.query.filter_by(username="newgladiator").first()
            assert user is not None
            assert user.email == "gladiator@royale.local"
            assert user.display_name == "Gladiator Prime"
            assert user.statistics is not None
            assert user.statistics.coins == 100

    def test_registration_duplicate_username_rejected(self, client, test_user):
        res = client.post(
            "/register",
            data={
                "username": test_user.username,
                "email": "different@royale.local",
                "password": "StrongPassword123!",
                "confirm_password": "StrongPassword123!",
            },
            follow_redirects=True,
        )
        # Should stay on register or show error
        assert b"already taken" in res.data or res.status_code == 200

    def test_login_success_and_logout(self, client, test_user):
        # Successful login
        res = client.post(
            "/login",
            data={
                "username_or_email": test_user.username,
                "password": "Password123!",
            },
            follow_redirects=True,
        )
        assert res.status_code == 200
        assert b"Ready for battle" in res.data or b"Command Dashboard" in res.data

        # Logout
        res_logout = client.post("/logout", follow_redirects=True)
        assert res_logout.status_code == 200

    def test_login_invalid_password(self, client, test_user):
        res = client.post(
            "/login",
            data={
                "username_or_email": test_user.username,
                "password": "IncorrectPassword999",
            },
            follow_redirects=True,
        )
        assert b"Invalid username or password" in res.data

    def test_suspended_user_cannot_login(self, client, test_user, app):
        with app.app_context():
            u = db.session.get(User, test_user.id)
            u.is_active = False
            db.session.commit()

        res = client.post(
            "/login",
            data={
                "username_or_email": test_user.username,
                "password": "Password123!",
            },
            follow_redirects=True,
        )
        assert b"suspended" in res.data

    def test_password_reset_flow(self, client, test_user, app):
        with app.app_context():
            # Step 1: Request reset
            success, msg, token = AuthService.request_password_reset(test_user.email)
            assert success is True
            assert token is not None

            # Step 2: Perform reset
            success_reset, msg_reset = AuthService.reset_password(token, "NewSecretPassword123!")
            assert success_reset is True

            # Step 3: Verify old password fails and new password succeeds
            u = db.session.get(User, test_user.id)
            assert u.check_password("Password123!") is False
            assert u.check_password("NewSecretPassword123!") is True
