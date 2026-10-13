from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user


def admin_required(f):
    """Decorator ensuring current user is authenticated and has administrative privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access the administrative panel.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if not (current_user.is_admin or current_user.has_role("admin")):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def moderator_required(f):
    """Decorator ensuring user is moderator or admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to perform moderation actions.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if not (current_user.is_admin or current_user.has_role("admin") or current_user.has_role("moderator")):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
