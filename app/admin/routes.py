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
