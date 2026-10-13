from typing import Optional, Tuple, Dict
from app.extensions import db
from app.models.user import User
from app.models.achievement import PlayerAchievement
from app.repositories.user_repo import UserRepository
from app.repositories.stats_repo import StatsRepository
from app.repositories.game_repo import GameRepository

user_repo = UserRepository()
stats_repo = StatsRepository()
game_repo = GameRepository()


class PlayerProfileService:
    """Business operations for player profiles and account settings."""

    @staticmethod
    def update_profile(
        user_id: int,
        display_name: str,
        avatar_seed: str,
        bio: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Update display name, avatar seed, and bio."""
        user = user_repo.get_by_id(user_id)
        if not user:
            return False, "Player account not found."

        name = display_name.strip()
        if len(name) < 2 or len(name) > 30:
            return False, "Display name must be between 2 and 30 characters."

        user.display_name = name
        user.avatar_seed = avatar_seed.strip() or user.username
        user.bio = (bio.strip()[:250]) if bio else None

        db.session.commit()
        return True, "Player profile updated successfully."

    @staticmethod
    def change_password(
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> Tuple[bool, str]:
        """Verify current credentials and update password."""
        user = user_repo.get_by_id(user_id)
        if not user:
            return False, "Player account not found."

        if not user.check_password(current_password):
            return False, "Current password is incorrect."

        if len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        user.set_password(new_password)
        db.session.commit()
        return True, "Password has been successfully changed."

    @staticmethod
    def get_player_summary(user_id: int) -> Dict:
        """Fetch unified player dashboard snapshot."""
        user = user_repo.get_by_id(user_id)
        if not user:
            return {}

        stats = stats_repo.get_or_create_stats(user_id)
        rank = stats_repo.get_user_rank(user_id)
        recent_matches = (
            db.session.query(game_repo.model)
            .filter_by(user_id=user_id, status="completed")
            .order_by(game_repo.model.completed_at.desc())
            .limit(5)
            .all()
        )
        unlocked_achievements_count = (
            db.session.query(PlayerAchievement).filter_by(user_id=user_id).count()
        )

        return {
            "user": user,
            "stats": stats,
            "rank": rank,
            "recent_matches": recent_matches,
            "unlocked_achievements_count": unlocked_achievements_count,
        }
