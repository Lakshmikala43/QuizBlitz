from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.question import Question
from app.models.session import MatchResult, QuizSession
from app.repositories.user_repo import UserRepository
from app.repositories.stats_repo import StatsRepository
from app.repositories.game_repo import GameRepository
from app.players.services import PlayerProfileService
from app.auth.forms import ChangePasswordForm

players_bp = Blueprint("players", __name__)
user_repo = UserRepository()
stats_repo = StatsRepository()
game_repo = GameRepository()


@players_bp.route("/")
def landing():
    """Public landing page with live dynamic platform statistics."""
    if current_user.is_authenticated:
        return redirect(url_for("players.dashboard"))

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


@players_bp.route("/dashboard")
@login_required
def dashboard():
    """Player command dashboard with stats, progression, and quick launch."""
    summary = PlayerProfileService.get_player_summary(current_user.id)
    featured_categories = (
        db.session.query(Category)
        .filter_by(is_active=True)
        .order_by(Category.sort_order.asc())
        .limit(6)
        .all()
    )

    return render_template(
        "players/dashboard.html",
        summary=summary,
        categories=featured_categories,
    )


@players_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Player profile view and update endpoint."""
    if request.method == "POST":
        display_name = request.form.get("display_name", "")
        avatar_seed = request.form.get("avatar_seed", "")
        bio = request.form.get("bio", "")

        success, message = PlayerProfileService.update_profile(
            user_id=current_user.id,
            display_name=display_name,
            avatar_seed=avatar_seed,
            bio=bio,
        )
        if success:
            flash(message, "success")
            return redirect(url_for("players.profile"))
        else:
            flash(message, "danger")

    stats = stats_repo.get_or_create_stats(current_user.id)
    rank = stats_repo.get_user_rank(current_user.id)
    return render_template("players/profile.html", stats=stats, rank=rank)


@players_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Account settings and credential updates."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        success, message = PlayerProfileService.change_password(
            user_id=current_user.id,
            current_password=form.current_password.data,
            new_password=form.new_password.data,
        )
        if success:
            flash(message, "success")
            return redirect(url_for("players.settings"))
        else:
            flash(message, "danger")

    return render_template("players/settings.html", form=form)


@players_bp.route("/history")
@login_required
def history():
    """Player battle history with pagination."""
    page = request.args.get("page", 1, type=int)
    history_data = game_repo.get_user_match_history(current_user.id, page=page, per_page=12)
    return render_template("players/history.html", history=history_data)
