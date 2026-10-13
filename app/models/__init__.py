"""Quiz Royale domain models package."""

from app.models.role import Role, UserRole
from app.models.user import User, load_user
from app.models.category import Category
from app.models.question import Question, AnswerOption
from app.models.session import (
    QuizSession,
    SessionQuestion,
    AnswerSubmission,
    MatchResult,
)
from app.models.multiplayer import MultiplayerRoom, RoomParticipant, generate_room_code
from app.models.statistics import PlayerStatistics
from app.models.achievement import Achievement, PlayerAchievement
from app.models.transaction import XPTransaction, RewardTransaction
from app.models.daily_challenge import DailyChallenge, DailyChallengeAttempt
from app.models.moderation import Report, Notification, AuditLog

__all__ = [
    "Role",
    "UserRole",
    "User",
    "load_user",
    "Category",
    "Question",
    "AnswerOption",
    "QuizSession",
    "SessionQuestion",
    "AnswerSubmission",
    "MatchResult",
    "MultiplayerRoom",
    "RoomParticipant",
    "generate_room_code",
    "PlayerStatistics",
    "Achievement",
    "PlayerAchievement",
    "XPTransaction",
    "RewardTransaction",
    "DailyChallenge",
    "DailyChallengeAttempt",
    "Report",
    "Notification",
    "AuditLog",
]
