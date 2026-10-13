"""
WSGI and ASGI production entrypoint for Quiz Royale.
Exposes both the core WSGI application and the Flask-SocketIO runtime server.
"""

import os
from app import create_app
from app.extensions import socketio

# Determine runtime environment from environment variable
environment = os.getenv("FLASK_ENV", "production")

# Instantiate configured application factory
app = create_app(config_name=environment)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    # In direct execution, utilize SocketIO standalone server
    socketio.run(app, host=host, port=port, debug=False)
