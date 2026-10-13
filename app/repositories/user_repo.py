from datetime import datetime, timezone
from typing import Optional, Dict
from sqlalchemy import or_
from app.extensions import db
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.statistics import PlayerStatistics
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data-access repository for User entities."""

    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Fetch user by case-insensitive username."""
        return db.session.query(User).filter(User.username.ilike(username.strip())).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by case-insensitive email."""
        return db.session.query(User).filter(User.email.ilike(email.strip())).first()

    def get_by_reset_token(self, token: str) -> Optional[User]:
        """Fetch user by reset token."""
        return db.session.query(User).filter_by(reset_token=token).first()

    def search_users(
        self,
        query_text: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict:
        """Search and paginate users for the admin dashboard."""
        q = db.session.query(User)

        if query_text:
            s = f"%{query_text.strip()}%"
            q = q.filter(or_(User.username.ilike(s), User.email.ilike(s), User.display_name.ilike(s)))

        if is_active is not None:
            q = q.filter(User.is_active == is_active)

        q = q.order_by(User.created_at.desc())
        return self.paginate(q, page=page, per_page=per_page)

    def update_last_login(self, user_id: int) -> None:
        """Record login timestamp."""
        user = self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()

    def assign_role(self, user: User, role_name: str) -> None:
        """Assign role to user if not already present."""
        role = db.session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
            db.session.flush()

        existing = (
            db.session.query(UserRole)
            .filter_by(user_id=user.id, role_id=role.id)
            .first()
        )
        if not existing:
            ur = UserRole(user_id=user.id, role_id=role.id)
            db.session.add(ur)
            db.session.commit()

    def remove_role(self, user: User, role_name: str) -> None:
        """Remove a role assignment from user."""
        role = db.session.query(Role).filter_by(name=role_name).first()
        if role:
            db.session.query(UserRole).filter_by(user_id=user.id, role_id=role.id).delete()
            db.session.commit()

    def toggle_active_status(self, user_id: int) -> Optional[User]:
        """Invert the is_active status of a user (suspend / reactivate)."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = not user.is_active
            db.session.commit()
        return user
