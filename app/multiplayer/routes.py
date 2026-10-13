from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.multiplayer.manager import room_manager
from app.repositories import CategoryRepository
from app.models.multiplayer import MultiplayerRoom

multiplayer_bp = Blueprint("multiplayer", __name__, url_prefix="/multiplayer")
category_repo = CategoryRepository()


@multiplayer_bp.route("/lobby")
@login_required
def lobby():
    """Multiplayer matchmaking lobby with active waiting rooms."""
    categories = category_repo.get_active_categories()
    # Query database for open rooms
    open_rooms = (
        MultiplayerRoom.query.filter_by(status="waiting")
        .order_by(MultiplayerRoom.created_at.desc())
        .limit(15)
        .all()
    )
    return render_template(
        "multiplayer/lobby.html",
        categories=categories,
        open_rooms=open_rooms,
    )


@multiplayer_bp.route("/create", methods=["POST"])
@login_required
def create_room():
    """Create a new multiplayer battle room."""
    category_slug = request.form.get("category", "all")
    difficulty = request.form.get("difficulty", "medium")
    question_count = request.form.get("question_count", 10, type=int)
    max_players = request.form.get("max_players", 8, type=int)

    code = room_manager.create_room(
        host_user=current_user,
        category_slug=category_slug,
        difficulty=difficulty,
        question_count=question_count,
        max_players=max_players,
    )

    return redirect(url_for("multiplayer.view_room", room_code=code))


@multiplayer_bp.route("/room/<room_code>")
@login_required
def view_room(room_code):
    """Live multiplayer battle room."""
    code = room_code.strip().upper()
    return render_template("multiplayer/room.html", room_code=code)
