from flask import Blueprint, render_template
from flask_login import current_user
from app.repositories import StatsRepository

achievements_bp = Blueprint("achievements", __name__, url_prefix="/achievements")
stats_repo = StatsRepository()


@achievements_bp.route("/")
def list_achievements():
    """Showcase of all platform achievement badges with player progress."""
    user_id = current_user.id if current_user.is_authenticated else None
    achievements = stats_repo.get_achievements_with_user_status(user_id) if user_id else []

    if not user_id:
        # Fallback for unauthenticated visitors
        from app.models.achievement import Achievement
        achievements = [a.to_dict() for a in Achievement.query.all()]

    unlocked_count = sum(1 for a in achievements if a.get("is_unlocked"))
    total_count = len(achievements)

    return render_template(
        "achievements/index.html",
        achievements=achievements,
        unlocked_count=unlocked_count,
        total_count=total_count,
    )
