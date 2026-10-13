import os
from flask import Flask, render_template
from app.config import CONFIG_MAP
from app.extensions import db, migrate, login_manager, csrf, socketio


def create_app(config_name=None):
    """Application factory for Quiz Royale."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    config_class = CONFIG_MAP.get(config_name, CONFIG_MAP["default"])
    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS", "*"),
        async_mode=app.config.get("SOCKETIO_ASYNC_MODE", "threading"),
    )

    # Register blueprints safely
    _register_blueprints(app)

    # Register global context processors & template filters
    _register_context_processors(app)

    # Register centralized error handlers
    _register_error_handlers(app)

    # Initialize defense-in-depth security headers and timers
    from app.security import init_security
    init_security(app)

    return app



def _register_blueprints(app):
    """Registers application blueprints if they are defined."""
    # We will import and register blueprints modularly
    try:
        from app.auth.routes import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError:
        pass

    try:
        from app.players.routes import players_bp
        app.register_blueprint(players_bp)
    except ImportError:
        pass

    try:
        from app.categories.routes import categories_bp
        app.register_blueprint(categories_bp)
    except ImportError:
        pass

    try:
        from app.games.routes import games_bp
        app.register_blueprint(games_bp)
    except ImportError:
        pass

    try:
        from app.leaderboards.routes import leaderboards_bp
        app.register_blueprint(leaderboards_bp)
    except ImportError:
        pass

    try:
        from app.achievements.routes import achievements_bp
        app.register_blueprint(achievements_bp)
    except ImportError:
        pass

    try:
        from app.multiplayer.routes import multiplayer_bp
        app.register_blueprint(multiplayer_bp)
    except ImportError:
        pass

    try:
        from app.admin.routes import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        pass

    try:
        from app.api.routes import api_bp
        app.register_blueprint(api_bp)
    except ImportError:
        pass


def _register_context_processors(app):
    """Context processors providing application-wide variables."""
    @app.context_processor
    def inject_app_context():
        return {
            "app_name": "Quiz Royale",
            "app_version": "1.0.0",
        }


def _register_error_handlers(app):
    """Register centralized error handlers supporting both HTML views and API JSON responses."""
    from flask import request, jsonify

    def _format_error(code: int, name: str, description: str, template: str):
        if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
            return jsonify({
                "status": "error",
                "code": code,
                "error": name,
                "message": description,
            }), code
        return render_template(template), code

    @app.errorhandler(403)
    def forbidden(e):
        return _format_error(403, "Forbidden", "You do not have permission to access this resource.", "errors/403.html")

    @app.errorhandler(404)
    def page_not_found(e):
        return _format_error(404, "Not Found", "The requested resource was not found on this server.", "errors/404.html")

    @app.errorhandler(429)
    def too_many_requests(e):
        return _format_error(429, "Too Many Requests", "Rate limit exceeded. Please wait before retrying.", "errors/429.html")

    @app.errorhandler(500)
    def internal_server_error(e):
        return _format_error(500, "Internal Server Error", "An unexpected system error occurred on the server.", "errors/500.html")

