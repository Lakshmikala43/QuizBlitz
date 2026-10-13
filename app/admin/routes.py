import os
import json
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.auth.decorators import admin_required
from app.models import (
    User,
    Category,
    Question,
    AnswerOption,
    MatchResult,
    Report,
    AuditLog,
)
from app.repositories import UserRepository, QuestionRepository, CategoryRepository

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
user_repo = UserRepository()
question_repo = QuestionRepository()
category_repo = CategoryRepository()


def log_admin_action(action_type: str, target_entity: str, target_id: str, details: dict):
    """Record administrative operation into the immutable audit trail."""
    try:
        log = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action_type=action_type,
            target_entity=target_entity,
            target_id=str(target_id),
            details_json=json.dumps(details),
            ip_address=request.remote_addr,
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()


@admin_bp.route("/")
@admin_required
def dashboard():
    """Admin central dashboard with operational metrics and health status."""
    total_users = db.session.query(func.count(User.id)).scalar() or 0
    total_active_users = db.session.query(func.count(User.id)).filter_by(is_active=True).scalar() or 0
    total_questions = db.session.query(func.count(Question.id)).scalar() or 0
    total_published_q = db.session.query(func.count(Question.id)).filter_by(is_published=True).scalar() or 0
    total_categories = db.session.query(func.count(Category.id)).scalar() or 0
    total_matches = db.session.query(func.count(MatchResult.id)).scalar() or 0
    pending_reports = db.session.query(func.count(Report.id)).filter_by(status="pending").scalar() or 0

    recent_logs = (
        db.session.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(8)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_active_users=total_active_users,
        total_questions=total_questions,
        total_published_q=total_published_q,
        total_categories=total_categories,
        total_matches=total_matches,
        pending_reports=pending_reports,
        recent_logs=recent_logs,
    )


# --- Category Management ---
@admin_bp.route("/categories")
@admin_required
def list_categories():
    """Admin categories overview."""
    categories = db.session.query(Category).order_by(Category.sort_order.asc(), Category.name.asc()).all()
    return render_template("admin/categories.html", categories=categories)


@admin_bp.route("/categories/create", methods=["POST"])
@admin_required
def create_category():
    """Add a new category."""
    name = request.form.get("name", "").strip()
    slug = request.form.get("slug", "").strip().lower()
    description = request.form.get("description", "").strip()
    color_hex = request.form.get("color_hex", "#6366f1").strip()
    sort_order = request.form.get("sort_order", 0, type=int)

    if not name or not slug:
        flash("Category name and slug are required.", "danger")
        return redirect(url_for("admin.list_categories"))

    if category_repo.get_by_slug(slug):
        flash("A category with this slug already exists.", "warning")
        return redirect(url_for("admin.list_categories"))

    cat = Category(
        name=name,
        slug=slug,
        description=description,
        color_hex=color_hex,
        sort_order=sort_order,
        is_active=True,
    )
    db.session.add(cat)
    db.session.commit()
    log_admin_action("create_category", "category", cat.id, {"name": name, "slug": slug})
    flash(f"Category '{name}' created successfully!", "success")
    return redirect(url_for("admin.list_categories"))


@admin_bp.route("/categories/<int:cat_id>/edit", methods=["POST"])
@admin_required
def edit_category(cat_id):
    """Update existing category details."""
    cat = category_repo.get_by_id(cat_id)
    if not cat:
        abort(404)

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    color_hex = request.form.get("color_hex", "#6366f1").strip()
    sort_order = request.form.get("sort_order", 0, type=int)

    if name:
        cat.name = name
    cat.description = description
    cat.color_hex = color_hex
    cat.sort_order = sort_order

    db.session.commit()
    log_admin_action("update_category", "category", cat.id, {"name": name})
    flash(f"Category '{cat.name}' updated.", "success")
    return redirect(url_for("admin.list_categories"))


@admin_bp.route("/categories/<int:cat_id>/toggle", methods=["POST"])
@admin_required
def toggle_category(cat_id):
    """Toggle category active status."""
    cat = category_repo.get_by_id(cat_id)
    if cat:
        cat.is_active = not cat.is_active
        db.session.commit()
        log_admin_action("toggle_category", "category", cat.id, {"is_active": cat.is_active})
        flash(f"Category active state toggled to {cat.is_active}.", "info")
    return redirect(url_for("admin.list_categories"))


# --- Question Management ---
@admin_bp.route("/questions")
@admin_required
def list_questions():
    """Admin questions listing with category, difficulty filters and search."""
    page = request.args.get("page", 1, type=int)
    category_id = request.args.get("category_id", type=int)
    difficulty = request.args.get("difficulty")
    search = request.args.get("search")

    paginated = question_repo.search_questions(
        category_id=category_id,
        difficulty=difficulty,
        search_text=search,
        page=page,
        per_page=15,
    )

    categories = category_repo.get_all()

    return render_template(
        "admin/questions.html",
        questions=paginated,
        categories=categories,
        selected_cat=category_id,
        selected_diff=difficulty,
        search=search or "",
    )


@admin_bp.route("/questions/create", methods=["GET", "POST"])
@admin_required
def create_question():
    """Create a new question with 4 options."""
    categories = category_repo.get_all()

    if request.method == "POST":
        q_text = request.form.get("question_text", "").strip()
        cat_id = request.form.get("category_id", type=int)
        difficulty = request.form.get("difficulty", "medium")
        explanation = request.form.get("explanation", "").strip()
        points = request.form.get("points", 100, type=int)
        time_limit = request.form.get("time_limit_sec", 15, type=int)
        correct_index = request.form.get("correct_option", 0, type=int)

        opt_texts = [
            request.form.get(f"option_{i}", "").strip()
            for i in range(4)
        ]

        if len(q_text) < 10:
            flash("Question text must be at least 10 characters.", "danger")
            return render_template("admin/question_edit.html", categories=categories, question=None)

        if any(len(t) < 1 for t in opt_texts):
            flash("All 4 option choices must have text.", "danger")
            return render_template("admin/question_edit.html", categories=categories, question=None)

        if question_repo.detect_duplicate_question(q_text):
            flash("An identical question already exists in the database.", "warning")
            return render_template("admin/question_edit.html", categories=categories, question=None)

        q_data = {
            "category_id": cat_id,
            "question_text": q_text,
            "difficulty": difficulty,
            "explanation": explanation,
            "points": points,
            "time_limit_sec": time_limit,
            "is_published": True,
        }
        options_data = [
            {"option_text": opt_texts[i], "is_correct": (i == correct_index), "order_index": i}
            for i in range(4)
        ]

        q = question_repo.create_question_with_options(q_data, options_data)
        log_admin_action("create_question", "question", q.id, {"text": q_text[:50]})
        flash(f"Question #{q.id} created successfully!", "success")
        return redirect(url_for("admin.list_questions"))

    return render_template("admin/question_edit.html", categories=categories, question=None)


@admin_bp.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_question(question_id):
    """Edit existing question and options."""
    question = question_repo.get_by_id(question_id)
    if not question:
        abort(404)

    categories = category_repo.get_all()

    if request.method == "POST":
        q_text = request.form.get("question_text", "").strip()
        cat_id = request.form.get("category_id", type=int)
        difficulty = request.form.get("difficulty", "medium")
        explanation = request.form.get("explanation", "").strip()
        points = request.form.get("points", 100, type=int)
        time_limit = request.form.get("time_limit_sec", 15, type=int)
        correct_index = request.form.get("correct_option", 0, type=int)

        opt_texts = [
            request.form.get(f"option_{i}", "").strip()
            for i in range(4)
        ]

        q_data = {
            "category_id": cat_id,
            "question_text": q_text,
            "difficulty": difficulty,
            "explanation": explanation,
            "points": points,
            "time_limit_sec": time_limit,
        }
        options_data = [
            {"option_text": opt_texts[i], "is_correct": (i == correct_index), "order_index": i}
            for i in range(4)
        ]

        question_repo.update_question_with_options(question.id, q_data, options_data)
        log_admin_action("update_question", "question", question.id, {"text": q_text[:50]})
        flash(f"Question #{question.id} updated successfully!", "success")
        return redirect(url_for("admin.list_questions"))

    return render_template("admin/question_edit.html", categories=categories, question=question)


@admin_bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@admin_required
def delete_question(question_id):
    """Delete a question."""
    question = question_repo.get_by_id(question_id)
    if question:
        log_admin_action("delete_question", "question", question.id, {"text": question.question_text[:50]})
        question_repo.delete(question)
        flash("Question deleted successfully.", "info")
    return redirect(url_for("admin.list_questions"))


@admin_bp.route("/questions/<int:question_id>/toggle-publish", methods=["POST"])
@admin_required
def toggle_publish_question(question_id):
    """Toggle publication status."""
    question = question_repo.get_by_id(question_id)
    if question:
        question.is_published = not question.is_published
        db.session.commit()
        log_admin_action("toggle_publish", "question", question.id, {"is_published": question.is_published})
        flash(f"Question publication set to {question.is_published}.", "success")
    return redirect(url_for("admin.list_questions"))
