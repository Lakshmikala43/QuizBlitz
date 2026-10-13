import sys
from datetime import datetime, timezone
from flask import current_app
from app.api import api_bp, success_response


@api_bp.route("/health")
def health_check():
    """Engine liveness probe."""
    return success_response(
        data={
            "status": "healthy",
            "service": "Quiz Royale Gameplay Engine",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        message="System operational",
    )


@api_bp.route("/status")
def system_status():
    """Engine runtime diagnostics and telemetry."""
    return success_response(
        data={
            "environment": current_app.config.get("ENV", "production"),
            "python_version": sys.version.split()[0],
            "database": "connected",
            "socketio_mode": current_app.config.get("SOCKETIO_ASYNC_MODE", "threading"),
            "features": {
                "multiplayer": True,
                "daily_challenge": True,
                "synthesized_audio": True,
                "zero_external_api_keys": True,
            },
        },
        message="Platform telemetry nominal",
    )


# --- Authentication & Session APIs ---
from flask import request
from flask_login import login_user, logout_user, current_user
from app.api import error_response, api_auth_required
from app.auth.services import AuthService
from app.security import rate_limit


@api_bp.route("/auth/register", methods=["POST"])
@rate_limit(requests=20, window_sec=60, bucket="api_auth_register")
def api_register():
    """Register a new player account."""
    data = request.get_json(silent=True) or request.form.to_dict()
    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")
    display_name = data.get("display_name", "")

    if not username or not email or not password:
        return error_response(
            message="Username, email, and password are required fields.",
            status_code=422,
            error_code="VALIDATION_ERROR",
        )

    success, msg, user = AuthService.register_user(
        username=username,
        email=email,
        password=password,
        display_name=display_name,
    )

    if not success or not user:
        return error_response(message=msg, status_code=400, error_code="REGISTRATION_FAILED")

    # Automatically establish session
    login_user(user)

    return success_response(
        data={
            "user": user.to_dict(),
        },
        message="Account registered successfully.",
        status_code=201,
    )


@api_bp.route("/auth/login", methods=["POST"])
@rate_limit(requests=30, window_sec=60, bucket="api_auth_login")
def api_login():
    """Authenticate player credentials and initiate session."""
    data = request.get_json(silent=True) or request.form.to_dict()
    identifier = data.get("login_identifier") or data.get("username") or data.get("email") or ""
    password = data.get("password", "")
    remember = bool(data.get("remember", False))

    if not identifier or not password:
        return error_response(
            message="Login identifier and password are required.",
            status_code=422,
            error_code="VALIDATION_ERROR",
        )

    success, msg, user = AuthService.authenticate_user(
        username_or_email=identifier,
        password=password,
    )

    if not success or not user:
        return error_response(message=msg, status_code=401, error_code="INVALID_CREDENTIALS")

    login_user(user, remember=remember)

    return success_response(
        data={
            "user": user.to_dict(),
        },
        message="Authentication successful.",
    )


@api_bp.route("/auth/logout", methods=["POST"])
@api_auth_required
def api_logout():
    """Terminate the active player session."""
    logout_user()
    return success_response(message="Logged out successfully.")


@api_bp.route("/auth/me")
@api_auth_required
def api_current_user():
    """Retrieve profile and stats of the currently authenticated player."""
    user_dict = current_user.to_dict()
    stats = current_user.statistics
    user_dict["stats"] = {
        "level": stats.level if stats else 1,
        "xp": stats.total_xp if stats else 0,
        "coins": stats.coins if stats else 0,
        "daily_streak": stats.daily_streak if stats else 0,
        "highest_streak": stats.highest_streak if stats else 0,
        "total_matches": stats.total_matches if stats else 0,
        "wins": stats.wins if stats else 0,
        "win_rate": stats.win_rate_percentage if stats else 0.0,
        "accuracy": stats.accuracy_percentage if stats else 0.0,
    }
    return success_response(data={"user": user_dict})


# --- Categories APIs ---
from app.repositories import CategoryRepository
from app.models.question import Question
from app.extensions import db
from sqlalchemy import func

category_repo = CategoryRepository()


@api_bp.route("/categories")
def api_list_categories():
    """List all active quiz categories with question totals."""
    categories = category_repo.get_active_categories()
    data = [c.to_dict() for c in categories]
    return success_response(data=data, message="Categories retrieved successfully.")


@api_bp.route("/categories/<slug>")
def api_get_category(slug: str):
    """Retrieve detailed information and difficulty breakdown for a single category."""
    cat = category_repo.get_by_slug(slug.strip().lower())
    if not cat:
        return error_response(
            message=f"Category '{slug}' not found.",
            status_code=404,
            error_code="CATEGORY_NOT_FOUND",
        )

    cat_data = cat.to_dict()

    # Difficulty breakdown
    diff_counts = (
        db.session.query(Question.difficulty, func.count(Question.id))
        .filter(Question.category_id == cat.id, Question.is_published == True)
        .group_by(Question.difficulty)
        .all()
    )
    cat_data["difficulty_breakdown"] = {diff: count for diff, count in diff_counts}

    return success_response(data=cat_data)


# --- Questions APIs ---
from app.repositories import QuestionRepository
from app.api import api_admin_required, paginate_response

question_repo = QuestionRepository()


@api_bp.route("/questions/sample")
def api_sample_questions():
    """
    Retrieve a sample batch of published questions for practice or quick-fire challenge.
    Ensures answers are scrubbed of correctness to guarantee fair play.
    """
    category_slug = request.args.get("category", "").strip().lower()
    difficulty = request.args.get("difficulty", "mixed").strip().lower()
    count = min(request.args.get("count", 5, type=int), 20)

    category_id = None
    if category_slug:
        cat = category_repo.get_by_slug(category_slug)
        if cat:
            category_id = cat.id

    questions = question_repo.get_random_questions(
        category_id=category_id,
        difficulty=difficulty if difficulty in {"easy", "medium", "hard"} else None,
        count=count,
    )

    data = [q.to_client_dict(shuffle_options=True) for q in questions]
    return success_response(data=data, message=f"Retrieved {len(data)} sample questions.")


@api_bp.route("/questions/<int:question_id>")
def api_get_question(question_id: int):
    """Retrieve an individual question by ID."""
    q = question_repo.get_by_id(question_id)
    if not q or not q.is_published:
        return error_response(message="Question not found.", status_code=404, error_code="NOT_FOUND")

    # Admins get full schema including answers and explanations; players get scrubbed schema
    if current_user.is_authenticated and getattr(current_user, "is_admin", False):
        return success_response(data=q.to_admin_dict())
    return success_response(data=q.to_client_dict(shuffle_options=False))


@api_bp.route("/questions")
@api_admin_required
def api_admin_search_questions():
    """Administrative search and pagination over the full question bank."""
    search = request.args.get("q", "")
    category_id = request.args.get("category_id", type=int)
    difficulty = request.args.get("difficulty", "")
    page = request.args.get("page", 1, type=int)

    pagination = question_repo.search_questions(
        query_text=search if search else None,
        category_id=category_id,
        difficulty=difficulty if difficulty else None,
        page=page,
        per_page=20,
    )

    items = [q.to_admin_dict() for q in pagination.get("items", [])]
    return success_response(
        data=items,
        meta={
            "page": pagination.get("page", 1),
            "pages": pagination.get("pages", 1),
            "total": pagination.get("total", 0),
        },
    )




