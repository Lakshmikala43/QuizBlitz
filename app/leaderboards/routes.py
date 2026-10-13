from flask import Blueprint, render_template, request
from app.repositories import StatsRepository, CategoryRepository

leaderboards_bp = Blueprint("leaderboards", __name__, url_prefix="/leaderboards")
stats_repo = StatsRepository()
category_repo = CategoryRepository()


@leaderboards_bp.route("/")
def view_leaderboard():
    """Global rankings view across daily, weekly, and all-time timeframes."""
    timeframe = request.args.get("timeframe", "all_time")
    if timeframe not in ("daily", "weekly", "all_time"):
        timeframe = "all_time"

    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    rankings = stats_repo.get_leaderboard(
        timeframe=timeframe,
        limit=limit,
        offset=offset,
    )

    categories = category_repo.get_active_categories()

    return render_template(
        "leaderboards/index.html",
        rankings=rankings,
        timeframe=timeframe,
        categories=categories,
    )
