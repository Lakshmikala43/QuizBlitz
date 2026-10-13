from typing import Optional, Tuple
from app.extensions import db
from app.models.user import User
from app.models.statistics import PlayerStatistics
from app.repositories.user_repo import UserRepository
from app.repositories.stats_repo import StatsRepository

user_repo = UserRepository()
stats_repo = StatsRepository()


class AuthService:
    """Business service for authentication, registration, and credential recovery."""

    @staticmethod
    def register_user(
        username: str,
        email: str,
        password: str,
        display_name: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[User]]:
        """Validate and create a new user account with initial statistics."""
        username = username.strip()
        email = email.strip().lower()

        if len(username) < 3 or len(username) > 30:
            return False, "Username must be between 3 and 30 characters.", None

        if len(password) < 6:
            return False, "Password must be at least 6 characters long.", None

        if user_repo.get_by_username(username):
            return False, "This username is already taken. Please choose another.", None

        if user_repo.get_by_email(email):
            return False, "An account with this email address already exists.", None

        # Create user
        user = User(
            username=username,
            email=email,
            display_name=display_name.strip() if display_name else username,
            avatar_seed=username,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        # Assign default player role
        user_repo.assign_role(user, "player")

        # Initialize player statistics
        stats_repo.get_or_create_stats(user.id)

        db.session.commit()
        return True, "Registration successful! You may now sign in.", user

    @staticmethod
    def authenticate_user(
        username_or_email: str,
        password: str,
    ) -> Tuple[bool, str, Optional[User]]:
        """Authenticate user against username or email and verify active status."""
        query_val = username_or_email.strip()
        user = user_repo.get_by_username(query_val) or user_repo.get_by_email(query_val)

        if not user:
            return False, "Invalid username or password.", None

        if not user.is_active:
            return False, "This account has been suspended. Please contact administration.", None

        if not user.check_password(password):
            return False, "Invalid username or password.", None

        # Record login timestamp
        user_repo.update_last_login(user.id)
        # Update daily login streak
        stats_repo.update_daily_login_streak(user.id)

        return True, "Authentication successful.", user

    @staticmethod
    def request_password_reset(email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Generate password reset token for local development flow.
        Returns: (success, message, token)
        """
        user = user_repo.get_by_email(email.strip())
        if not user:
            # For security, avoid disclosing non-existent emails
            return True, "If the email is registered, a password recovery link has been generated.", None

        token = user.generate_reset_token(expires_in_minutes=60)
        db.session.commit()
        return True, "Recovery link generated.", token

    @staticmethod
    def reset_password(token: str, new_password: str) -> Tuple[bool, str]:
        """Validate token and update password."""
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        user = user_repo.get_by_reset_token(token)
        if not user or not user.verify_reset_token(token):
            return False, "This password reset link is invalid or has expired."

        user.set_password(new_password)
        user.clear_reset_token()
        db.session.commit()
        return True, "Password has been successfully updated. You may now log in."
