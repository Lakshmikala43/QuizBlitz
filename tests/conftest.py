import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app import create_app

from app.extensions import db
from app.models import (
    User,
    Role,
    UserRole,
    Category,
    Question,
    AnswerOption,
    PlayerStatistics,
    Achievement,
)


@pytest.fixture(scope="session")
def app():
    """Create and configure an isolated Flask application instance for test suites."""
    application = create_app("testing")
    application.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key-12345",
    })

    with application.app_context():
        db.create_all()

        # Seed standard roles
        for r_name in ["admin", "moderator", "player"]:
            if not Role.query.filter_by(name=r_name).first():
                db.session.add(Role(name=r_name))
        db.session.commit()

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Test HTTP client."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Clean database state between test runs to ensure isolation."""
    yield
    with app.app_context():
        # Clear dynamic tables while preserving schema
        db.session.rollback()
        for table in reversed(db.metadata.sorted_tables):
            if table.name != "roles":
                db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def test_user(app):
    """Persisted regular player account fixture."""
    with app.app_context():
        user = User(
            username="testplayer",
            email="testplayer@example.com",
            display_name="Test Player",
            avatar_seed="testplayer",
            is_active=True,
            is_admin=False,
        )
        user.set_password("Password123!")
        db.session.add(user)
        db.session.flush()

        # Add stats
        stats = PlayerStatistics(user_id=user.id, coins=100, total_xp=50, level=1)
        db.session.add(stats)
        db.session.commit()
        return user


@pytest.fixture
def test_admin(app):
    """Persisted administrative user fixture."""
    with app.app_context():
        admin = User(
            username="testadmin",
            email="testadmin@example.com",
            display_name="Admin Overseer",
            avatar_seed="testadmin",
            is_active=True,
            is_admin=True,
        )
        admin.set_password("AdminPass123!")
        db.session.add(admin)
        db.session.flush()

        stats = PlayerStatistics(user_id=admin.id, coins=500, total_xp=1000, level=5)
        db.session.add(stats)
        db.session.commit()
        return admin


@pytest.fixture
def sample_category(app):
    """Persisted category fixture."""
    with app.app_context():
        cat = Category(
            name="Python Programming",
            slug="python",
            description="Core Python syntax, features, and standard libraries.",
            icon="terminal",
            color_hex="#4ade80",
            sort_order=1,
            is_active=True,
        )
        db.session.add(cat)
        db.session.commit()
        return cat


@pytest.fixture
def sample_questions(app, sample_category):
    """Persisted set of 5 sample questions with 4 options each."""
    questions = []
    with app.app_context():
        cat = Category.query.filter_by(slug="python").first()
        for i in range(1, 6):
            q = Question(
                category_id=cat.id,
                question_text=f"Sample Question {i}: What is the output of test case #{i}?",
                difficulty="medium",
                explanation=f"Educational explanation for question #{i}.",
                points=100,
                time_limit_sec=15,
                is_published=True,
            )
            db.session.add(q)
            db.session.flush()

            for opt_idx in range(4):
                is_correct = (opt_idx == 0)
                opt = AnswerOption(
                    question_id=q.id,
                    option_text=f"Option {chr(65 + opt_idx)} for Q{i}" + (" (Correct)" if is_correct else ""),
                    is_correct=is_correct,
                    order_index=opt_idx,
                )
                db.session.add(opt)

            questions.append(q)
        db.session.commit()
        return questions
