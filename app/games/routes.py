from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.games.services import QuizSessionService
from app.repositories import GameRepository, CategoryRepository, QuestionRepository
from app.models.daily_challenge import DailyChallenge, DailyChallengeAttempt
from app.extensions import db

games_bp = Blueprint("games", __name__, url_prefix="/play")
game_repo = GameRepository()
category_repo = CategoryRepository()
question_repo = QuestionRepository()


@games_bp.route("/modes")
def select_mode():
    """Showcase of available game modes."""
    return render_template("games/modes.html")


@games_bp.route("/setup")
@login_required
def setup_match():
    """Configure category, difficulty, question volume, and launch match."""
    selected_mode = request.args.get("mode", "solo")
    selected_cat = request.args.get("category", "all")
    selected_diff = request.args.get("difficulty", "mixed")

    categories = category_repo.get_active_categories()
    return render_template(
        "games/setup.html",
        categories=categories,
        mode=selected_mode,
        selected_category=selected_cat,
        selected_difficulty=selected_diff,
    )


@games_bp.route("/start", methods=["POST"])
@login_required
def start_game():
    """Initialize a new game session and redirect to the gameplay arena."""
    category_slug = request.form.get("category", "all")
    difficulty = request.form.get("difficulty", "mixed")
    question_count = request.form.get("question_count", 10, type=int)
    game_mode = request.form.get("game_mode", "solo")

    success, message, session = QuizSessionService.start_session(
        user_id=current_user.id,
        category_slug=category_slug,
        difficulty=difficulty,
        question_count=question_count,
        game_mode=game_mode,
    )

    if not success or not session:
        flash(message, "danger")
        return redirect(url_for("games.setup_match"))

    return redirect(url_for("games.play_view", session_id=session.id))


@games_bp.route("/<session_id>")
@login_required
def play_view(session_id):
    """Active gameplay arena view."""
    session = game_repo.get_by_id(session_id)
    if not session or session.user_id != current_user.id:
        abort(404)

    if session.is_finished:
        return redirect(url_for("games.results_view", session_id=session.id))

    return render_template("games/play.html", session=session)


@games_bp.route("/<session_id>/question")
@login_required
def get_question_api(session_id):
    """JSON API to fetch current question safely without exposing answers."""
    success, message, payload = QuizSessionService.get_current_question_payload(
        session_id=session_id,
        user_id=current_user.id,
    )
    if not success:
        return jsonify({"success": False, "error": message}), 400

    return jsonify({"success": True, "data": payload})


@games_bp.route("/<session_id>/submit", methods=["POST"])
@login_required
def submit_answer_api(session_id):
    """JSON API to authoritatively evaluate submitted answer."""
    data = request.get_json() or {}
    question_id = data.get("question_id")
    selected_option_id = data.get("selected_option_id")  # May be None for timeout
    idempotency_key = data.get("idempotency_key")

    if not question_id:
        return jsonify({"success": False, "error": "Question ID is required."}), 400

    success, message, result = QuizSessionService.submit_answer(
        session_id=session_id,
        user_id=current_user.id,
        question_id=question_id,
        selected_option_id=selected_option_id,
        idempotency_key=idempotency_key,
    )

    if not success:
        return jsonify({"success": False, "error": message}), 400

    return jsonify({"success": True, "data": result})


@games_bp.route("/<session_id>/next", methods=["POST"])
@login_required
def advance_question_api(session_id):
    """JSON API to transition to the next question or finalize match."""
    success, is_finished = QuizSessionService.advance_session(
        session_id=session_id,
        user_id=current_user.id,
    )

    if not success:
        return jsonify({"success": False, "error": "Unable to advance question."}), 400

    return jsonify({"success": True, "is_finished": is_finished})


@games_bp.route("/<session_id>/results")
@login_required
def results_view(session_id):
    """Match completion screen with analytics and rewards."""
    session = game_repo.get_by_id(session_id)
    if not session or session.user_id != current_user.id:
        abort(404)

    result = session.match_result
    return render_template("games/results.html", session=session, result=result)


@games_bp.route("/<session_id>/review")
@login_required
def review_view(session_id):
    """Review screen displaying all questions with options and explanations."""
    session = game_repo.get_by_id(session_id)
    if not session or session.user_id != current_user.id:
        abort(404)

    return render_template("games/review.html", session=session)


@games_bp.route("/daily")
@login_required
def daily_challenge_view():
    """Daily challenge overview and status."""
    today = datetime.now(timezone.utc).date()
    challenge = DailyChallenge.query.filter_by(challenge_date=today).first()
    if not challenge:
        # Create deterministic daily challenge for today
        challenge = DailyChallenge(
            challenge_date=today,
            title=f"Royale Daily Trial — {today.strftime('%B %d')}",
            description="10 curated questions across diverse disciplines. One ranked shot at glory!",
            bonus_xp=300,
            bonus_coins=150,
        )
        db.session.add(challenge)
        db.session.commit()

    # Check if player already completed today's challenge
    attempt = DailyChallengeAttempt.query.filter_by(
        challenge_id=challenge.id,
        user_id=current_user.id,
    ).first()

    # Leaderboard for today's challenge
    today_attempts = (
        DailyChallengeAttempt.query.filter_by(challenge_id=challenge.id)
        .order_by(DailyChallengeAttempt.score.desc())
        .limit(20)
        .all()
    )

    return render_template(
        "games/daily_challenge.html",
        challenge=challenge,
        attempt=attempt,
        leaderboard=today_attempts,
    )


@games_bp.route("/report-question", methods=["POST"])
@login_required
def report_question():
    """Allow players to report or flag problematic questions during match review."""
    from app.models.moderation import Report

    question_id = request.form.get("question_id", type=int)
    reason = request.form.get("reason", "").strip()
    details = request.form.get("details", "").strip()
    session_id = request.form.get("session_id", "")

    if not question_id or not reason:
        flash("Please provide a reason for reporting this question.", "warning")
        if session_id:
            return redirect(url_for("games.review_view", session_id=session_id))
        return redirect(url_for("players.dashboard"))

    # Verify question exists
    question = question_repo.get_by_id(question_id)
    if not question:
        flash("Question not found.", "danger")
        if session_id:
            return redirect(url_for("games.review_view", session_id=session_id))
        return redirect(url_for("players.dashboard"))

    # Check for duplicate pending report by same user
    existing = Report.query.filter_by(
        question_id=question_id,
        reporter_user_id=current_user.id,
        status="pending"
    ).first()

    if existing:
        flash("You have already submitted a pending report for this question.", "info")
    else:
        new_report = Report(
            question_id=question_id,
            reporter_user_id=current_user.id,
            reason=reason,
            details=details if details else None,
            status="pending",
        )
        db.session.add(new_report)
        db.session.commit()
        flash("Thank you! Your report has been submitted to moderators for review.", "success")

    if session_id:
        return redirect(url_for("games.review_view", session_id=session_id))
    return redirect(url_for("players.dashboard"))

