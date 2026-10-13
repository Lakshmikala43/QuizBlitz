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
    """Register centralized error handlers."""
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def too_many_requests(e):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500
