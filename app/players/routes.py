from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.question import Question
from app.models.session import MatchResult
from app.repositories.user_repo import UserRepository
from app.repositories.stats_repo import StatsRepository
from app.repositories.game_repo import GameRepository

players_bp = Blueprint("players", __name__)
user_repo = UserRepository()
stats_repo = StatsRepository()
game_repo = GameRepository()


@players_bp.route("/")
def landing():
    """Public landing page with live dynamic platform statistics."""
    if current_user.is_authenticated:
        return redirect(url_for("players.dashboard"))

    # Live platform stats
    total_players = db.session.query(func.count(User.id)).scalar() or 0
    total_questions = db.session.query(func.count(Question.id)).filter_by(is_published=True).scalar() or 0
    total_matches = db.session.query(func.count(MatchResult.id)).scalar() or 0
    categories = db.session.query(Category).filter_by(is_active=True).order_by(Category.sort_order.asc()).limit(8).all()

    return render_template(
        "players/landing.html",
        total_players=total_players,
        total_questions=total_questions,
        total_matches=total_matches,
        categories=categories,
    )


@players_bp.route("/help")
def help_page():
    """Platform rules, scoring guide, and FAQ."""
    return render_template("players/help.html")
