#!/usr/bin/env python3
"""
Quiz Royale — Database Initialization and Verification Script

Creates database tables and default roles in a clean, reproducible manner.
Enables SQLite foreign key constraints and WAL journal mode.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from app.models import Role


def init_database(config_name="development"):
    """Initialize database tables and base system roles."""
    print(f"Initializing Quiz Royale database with configuration [{config_name}]...")
    app = create_app(config_name)

    with app.app_context():
        # Enable SQLite foreign keys if using SQLite
        if "sqlite" in app.config.get("SQLALCHEMY_DATABASE_URI", ""):
            from sqlalchemy import event
            from sqlalchemy.engine import Engine

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.close()

        db.create_all()
        print(f"[OK] Database schema created. Total tables: {len(db.metadata.tables)}")

        # Seed standard roles if not present
        roles = [
            ("admin", "Platform administrator with full privileges"),
            ("moderator", "Content moderator capable of reviewing reports and questions"),
            ("player", "Standard competitive player"),
        ]

        created_count = 0
        for name, desc in roles:
            existing = Role.query.filter_by(name=name).first()
            if not existing:
                role = Role(name=name, description=desc)
                db.session.add(role)
                created_count += 1

        db.session.commit()
        print(f"[OK] Base roles verified. Added {created_count} new roles.")
        print("[SUCCESS] Database initialization completed.")


if __name__ == "__main__":
    cfg = sys.argv[1] if len(sys.argv) > 1 else "development"
    init_database(cfg)
