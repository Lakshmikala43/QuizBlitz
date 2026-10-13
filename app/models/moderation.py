import json
from datetime import datetime, timezone
from app.extensions import db


class Report(db.Model):
    """User-submitted flag or report on a question."""

    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = db.Column(db.String(64), nullable=False)  # incorrect_answer, typo, offensive, outdated
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(24), default="pending", nullable=False, index=True)  # pending, reviewed, resolved, dismissed
    admin_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    resolved_at = db.Column(db.DateTime, nullable=True)

    question = db.relationship("Question", back_populates="reports")
    reporter = db.relationship("User")

    def __repr__(self):
        return f"<Report #{self.id} for Q#{self.question_id} ({self.status})>"

    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "question_text": self.question.question_text if self.question else "Deleted",
            "reporter_user_id": self.reporter_user_id,
            "reporter_username": self.reporter.username if self.reporter else "Unknown",
            "reason": self.reason,
            "details": self.details,
            "status": self.status,
            "admin_notes": self.admin_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


class Notification(db.Model):
    """In-app player notification."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(32), default="system", nullable=False)  # level_up, achievement, reward, system
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    link_url = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    user = db.relationship("User")

    def __repr__(self):
        return f"<Notification #{self.id} user={self.user_id} ({self.notification_type})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "is_read": self.is_read,
            "link_url": self.link_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    """Audit trail for sensitive and administrative actions."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action_type = db.Column(db.String(64), nullable=False, index=True)  # create_question, delete_question, ban_user, etc.
    target_entity = db.Column(db.String(64), nullable=False)  # question, category, user, report
    target_id = db.Column(db.String(64), nullable=True)
    details_json = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    user = db.relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog #{self.id} user={self.user_id} action={self.action_type}>"

    def get_details(self) -> dict:
        if not self.details_json:
            return {}
        try:
            return json.loads(self.details_json)
        except Exception:
            return {"raw": self.details_json}

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "System",
            "action_type": self.action_type,
            "target_entity": self.target_entity,
            "target_id": self.target_id,
            "details": self.get_details(),
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
