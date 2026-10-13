from functools import wraps
from flask import Blueprint, jsonify, request, g
from flask_login import current_user
from app.extensions import csrf

api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
# Exempt REST API v1 from HTML form CSRF token validation
csrf.exempt(api_bp)


def success_response(data=None, message: str = "Success", status_code: int = 200, meta: dict = None):
    """Generate consistent JSON response for successful requests."""
    payload = {
        "status": "success",
        "message": message,
        "data": data if data is not None else {},
    }
    if meta:
        payload["meta"] = meta
    return jsonify(payload), status_code


def error_response(message: str = "An error occurred", status_code: int = 400, error_code: str = None, details=None):
    """Generate consistent JSON response for errors."""
    payload = {
        "status": "error",
        "message": message,
        "code": status_code,
    }
    if error_code:
        payload["error_code"] = error_code
    if details:
        payload["details"] = details
    return jsonify(payload), status_code


def paginate_response(pagination: dict, message: str = "Data retrieved successfully"):
    """Format standard paginated repository output into API envelope."""
    items = [item.to_dict() if hasattr(item, "to_dict") else item for item in pagination.get("items", [])]
    meta = {
        "page": pagination.get("page", 1),
        "pages": pagination.get("pages", 1),
        "total": pagination.get("total", len(items)),
        "has_prev": pagination.get("has_prev", False),
        "has_next": pagination.get("has_next", False),
    }
    return success_response(data=items, message=message, meta=meta)


def api_auth_required(f):
    """Enforce authentication on API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return error_response(
                message="Authentication required to access this endpoint.",
                status_code=401,
                error_code="UNAUTHORIZED",
            )
        return f(*args, **kwargs)
    return decorated


def api_admin_required(f):
    """Enforce administrator rank on API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return error_response(
                message="Authentication required to access this endpoint.",
                status_code=401,
                error_code="UNAUTHORIZED",
            )
        if not getattr(current_user, "is_admin", False):
            return error_response(
                message="Administrative privileges required.",
                status_code=403,
                error_code="FORBIDDEN",
            )
        return f(*args, **kwargs)
    return decorated


# Import sub-modules to register routes
from app.api import routes  # noqa: E402
