#!/usr/bin/env python3
"""
Quiz Royale — Master Database Seeder

Populates clean SQLite/PostgreSQL databases with:
1. System Roles (admin, moderator, player)
2. All 14 Categories
3. Standard Platform Achievements & Badges
4. Quality-assured Seed Question Bank with options
5. Preconfigured Administrator and Player accounts
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from app.models import (
    Role,
    User,
    Category,
    Question,
    AnswerOption,
    Achievement,
    PlayerStatistics,
)
from app.repositories import UserRepository, QuestionRepository, StatsRepository
from scripts.seed_data.programming import PROGRAMMING_CATEGORIES, PROGRAMMING_QUESTIONS
from scripts.seed_data.computer_science import CS_CATEGORIES, CS_QUESTIONS
from scripts.seed_data.general import GENERAL_CATEGORIES, GENERAL_QUESTIONS

user_repo = UserRepository()
question_repo = QuestionRepository()
stats_repo = StatsRepository()

ACHIEVEMENTS_DATA = [
    {
        "code": "first_blood",
        "title": "First Blood",
        "description": "Complete your very first quiz battle.",
        "icon": "award",
        "tier": "bronze",
        "xp_reward": 100,
        "coin_reward": 50,
        "requirement_type": "matches_played",
        "requirement_threshold": 1,
    },
    {
        "code": "streak_master",
        "title": "Streak Master",
        "description": "Achieve a consecutive streak of 5 correct answers in a single match.",
        "icon": "zap",
        "tier": "silver",
        "xp_reward": 250,
        "coin_reward": 100,
        "requirement_type": "streak",
        "requirement_threshold": 5,
    },
    {
        "code": "century_club",
        "title": "Century Club",
        "description": "Answer 100 total questions correctly across any game modes.",
        "icon": "target",
        "tier": "gold",
        "xp_reward": 500,
        "coin_reward": 250,
        "requirement_type": "correct_answers",
        "requirement_threshold": 100,
    },
    {
        "code": "polymath",
        "title": "Polymath",
        "description": "Reach Level 5 as an experienced Quiz Royale champion.",
        "icon": "shield",
        "tier": "gold",
        "xp_reward": 750,
        "coin_reward": 300,
        "requirement_type": "level",
        "requirement_threshold": 5,
    },
    {
        "code": "daily_warrior",
        "title": "Daily Devotion",
        "description": "Maintain a 3-day consecutive login streak.",
        "icon": "calendar",
        "tier": "silver",
        "xp_reward": 300,
        "coin_reward": 150,
        "requirement_type": "daily_streak",
        "requirement_threshold": 3,
    },
]


def seed_database(config_name="development"):
    app = create_app(config_name)

    with app.app_context():
        print(f"[*] Seeding Quiz Royale database [{config_name}]...")
        db.create_all()

        # 1. Seed Roles
        roles = {
            "admin": "Platform administrator with full privileges",
            "moderator": "Content moderator",
            "player": "Competitive player",
        }
        for name, desc in roles.items():
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, description=desc))
        db.session.commit()

        # 2. Seed Default Accounts
        # Admin account
        admin = user_repo.get_by_username("admin")
        if not admin:
            admin = User(
                username="admin",
                email="admin@quizroyale.local",
                display_name="Royal Overseer",
                avatar_seed="admin",
                is_admin=True,
                is_active=True,
                bio="Official Quiz Royale Platform Administrator",
            )
            admin.set_password("AdminRoyale2026!")
            db.session.add(admin)
            db.session.flush()
            user_repo.assign_role(admin, "admin")
            stats_repo.get_or_create_stats(admin.id)
            print("[+] Created Admin account: admin / AdminRoyale2026!")

        # Player account
        player = user_repo.get_by_username("player1")
        if not player:
            player = User(
                username="player1",
                email="player1@quizroyale.local",
                display_name="BladeRunner",
                avatar_seed="player1",
                is_admin=False,
                is_active=True,
                bio="Climbing the rankings to reach the grandmaster podium.",
            )
            player.set_password("PlayerRoyale2026!")
            db.session.add(player)
            db.session.flush()
            user_repo.assign_role(player, "player")
            stats = stats_repo.get_or_create_stats(player.id)
            stats.total_xp = 350
            stats.level = 2
            stats.coins = 200
            print("[+] Created Player account: player1 / PlayerRoyale2026!")

        # 3. Seed Achievements
        ach_count = 0
        for ach_dict in ACHIEVEMENTS_DATA:
            existing = Achievement.query.filter_by(code=ach_dict["code"]).first()
            if not existing:
                ach = Achievement(**ach_dict)
                db.session.add(ach)
                ach_count += 1
        db.session.commit()
        if ach_count:
            print(f"[+] Seeded {ach_count} platform achievements.")

        # 4. Seed Categories
        all_categories = PROGRAMMING_CATEGORIES + CS_CATEGORIES + GENERAL_CATEGORIES
        cat_map = {}
        cat_count = 0
        for c in all_categories:
            existing = Category.query.filter_by(slug=c["slug"]).first()
            if not existing:
                cat = Category(**c)
                db.session.add(cat)
                db.session.flush()
                cat_map[c["slug"]] = cat
                cat_count += 1
            else:
                cat_map[c["slug"]] = existing
        db.session.commit()
        if cat_count:
            print(f"[+] Seeded {cat_count} categories.")

        # 5. Seed Questions and Options
        all_questions = PROGRAMMING_QUESTIONS + CS_QUESTIONS + GENERAL_QUESTIONS
        q_count = 0
        for q in all_questions:
            existing = question_repo.detect_duplicate_question(q["question_text"])
            if not existing:
                cat = cat_map.get(q["category_slug"]) or Category.query.filter_by(slug=q["category_slug"]).first()
                if not cat:
                    continue

                question_data = {
                    "category_id": cat.id,
                    "question_text": q["question_text"],
                    "difficulty": q["difficulty"],
                    "explanation": q["explanation"],
                    "points": q["points"],
                    "time_limit_sec": q["time_limit_sec"],
                    "is_published": True,
                }
                options_data = [
                    {
                        "option_text": opt["text"],
                        "is_correct": opt["is_correct"],
                        "order_index": idx,
                    }
                    for idx, opt in enumerate(q["options"])
                ]
                question_repo.create_question_with_options(question_data, options_data)
                q_count += 1

        print(f"[+] Seeded {q_count} new questions with validated option sets.")
        print("[SUCCESS] Database seeding completed successfully!")


if __name__ == "__main__":
    cfg = sys.argv[1] if len(sys.argv) > 1 else "development"
    seed_database(cfg)
