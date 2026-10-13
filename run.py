import os
from app import create_app
from app.extensions import socketio

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"Starting Quiz Royale server at http://{host}:{port} ...")
    socketio.run(app, host=host, port=port, debug=app.config.get("DEBUG", True))
