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
