from datetime import datetime, timezone, date, timedelta
from typing import Optional, List, Dict, Tuple
from sqlalchemy import desc, func
from app.extensions import db
from app.models.statistics import PlayerStatistics
from app.models.achievement import Achievement, PlayerAchievement
from app.models.transaction import XPTransaction, RewardTransaction
from app.models.session import MatchResult
from app.models.user import User
from app.repositories.base import BaseRepository


class StatsRepository(BaseRepository[PlayerStatistics]):
    """Data-access repository for player statistics, leaderboards, and rewards."""

    def __init__(self):
        super().__init__(PlayerStatistics)

    def get_or_create_stats(self, user_id: int) -> PlayerStatistics:
        """Fetch statistics record or initialize a new record for a user."""
        stats = db.session.query(PlayerStatistics).filter_by(user_id=user_id).first()
        if not stats:
            stats = PlayerStatistics(user_id=user_id)
            db.session.add(stats)
            db.session.commit()
        return stats

    def apply_match_rewards(
        self,
        user_id: int,
        xp: int,
        coins: int,
        score: int,
        streak: int,
        correct_count: int,
        total_count: int,
        is_win: bool = False,
        session_id: Optional[str] = None,
    ) -> PlayerStatistics:
        """
        Incrementally update player totals, record audited ledger transactions,
        and recompute player level.
        """
        stats = self.get_or_create_stats(user_id)
        stats.total_xp += xp
        stats.coins += coins
        stats.total_matches += 1
        if is_win:
            stats.wins += 1
        stats.total_correct += correct_count
        stats.total_answered += total_count

        if score > stats.highest_score:
            stats.highest_score = score
        if streak > stats.highest_streak:
            stats.highest_streak = streak

        # Recompute level
        new_level = PlayerStatistics.calculate_level_from_xp(stats.total_xp)
        stats.level = new_level

        # Record ledger transactions
        if xp > 0:
            xp_txn = XPTransaction(
                user_id=user_id,
                amount=xp,
                source_type="match",
                reference_id=session_id,
                description=f"Match completed with score {score}",
            )
            db.session.add(xp_txn)

        if coins > 0:
            coin_txn = RewardTransaction(
                user_id=user_id,
                amount=coins,
                currency_type="coins",
                source_type="match",
                reference_id=session_id,
                description=f"Match rewards for score {score}",
            )
            db.session.add(coin_txn)

        db.session.commit()
        return stats

    def update_daily_login_streak(self, user_id: int) -> Tuple[bool, int, int]:
        """
        Evaluate daily login bonus.
        Returns: (awarded_today, current_streak, bonus_coins)
        """
        stats = self.get_or_create_stats(user_id)
        today = datetime.now(timezone.utc).date()

        if stats.last_active_date == today:
            # Already collected login today
            return False, stats.daily_streak, 0

        yesterday = today - timedelta(days=1)
        if stats.last_active_date == yesterday:
            stats.daily_streak += 1
        else:
            stats.daily_streak = 1

        stats.last_active_date = today

        # Scaled streak reward (base 25 + 5 * streak, capped at 100)
        bonus_coins = min(100, 25 + (stats.daily_streak * 5))
        stats.coins += bonus_coins

        # Record reward transaction
        txn = RewardTransaction(
            user_id=user_id,
            amount=bonus_coins,
            currency_type="coins",
            source_type="daily_login",
            description=f"Day {stats.daily_streak} login streak bonus",
        )
        db.session.add(txn)
        db.session.commit()

        return True, stats.daily_streak, bonus_coins

    def get_leaderboard(
        self,
        timeframe: str = "all_time",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict]:
        """
        Fetch ranked leaderboard.
        Supported timeframes: 'daily', 'weekly', 'all_time'.
        Tie-breaking rule: Score first, accuracy second, recency third.
        """
        now = datetime.now(timezone.utc)

        if timeframe == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return self._aggregate_match_leaderboard(start_date, limit, offset)
        elif timeframe == "weekly":
            start_date = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
            return self._aggregate_match_leaderboard(start_date, limit, offset)
        else:
            # All-time leaderboard based on total XP and Level
            query = (
                db.session.query(PlayerStatistics, User)
                .join(User, PlayerStatistics.user_id == User.id)
                .filter(User.is_active == True)
                .order_by(
                    PlayerStatistics.total_xp.desc(),
                    PlayerStatistics.highest_score.desc(),
                )
                .offset(offset)
                .limit(limit)
            )
            results = []
            for rank_idx, (stats, user) in enumerate(query.all(), start=offset + 1):
                results.append({
                    "rank": rank_idx,
                    "user_id": user.id,
                    "username": user.username,
                    "display_name": user.effective_display_name,
                    "avatar_seed": user.avatar_seed,
                    "level": stats.level,
                    "score": stats.total_xp,
                    "accuracy_pct": stats.accuracy_percentage,
                    "matches": stats.total_matches,
                })
            return results

    def _aggregate_match_leaderboard(
        self, start_date: datetime, limit: int, offset: int
    ) -> List[Dict]:
        """Aggregate total score from matches within a specific timeframe."""
        query = (
            db.session.query(
                User.id,
                User.username,
                User.display_name,
                User.avatar_seed,
                PlayerStatistics.level,
                func.sum(MatchResult.total_score).label("timeframe_score"),
                func.count(MatchResult.id).label("matches_count"),
                func.avg(MatchResult.accuracy_pct).label("avg_accuracy"),
            )
            .join(MatchResult, User.id == MatchResult.user_id)
            .join(PlayerStatistics, User.id == PlayerStatistics.user_id)
            .filter(MatchResult.recorded_at >= start_date, User.is_active == True)
            .group_by(User.id, PlayerStatistics.level)
            .order_by(desc("timeframe_score"))
            .offset(offset)
            .limit(limit)
        )

        entries = []
        for rank_idx, row in enumerate(query.all(), start=offset + 1):
            entries.append({
                "rank": rank_idx,
                "user_id": row[0],
                "username": row[1],
                "display_name": row[2] or row[1],
                "avatar_seed": row[3],
                "level": row[4],
                "score": int(row[5] or 0),
                "accuracy_pct": round(float(row[7] or 0.0), 1),
                "matches": int(row[6] or 0),
            })
        return entries

    def get_user_rank(self, user_id: int) -> int:
        """Calculate global all-time rank for a user."""
        user_stats = self.get_or_create_stats(user_id)
        higher_count = (
            db.session.query(PlayerStatistics)
            .filter(PlayerStatistics.total_xp > user_stats.total_xp)
            .count()
        )
        return higher_count + 1

    def get_achievements_with_user_status(self, user_id: int) -> List[Dict]:
        """Retrieve all platform achievements annotated with the user's unlock status."""
        all_achievements = db.session.query(Achievement).order_by(Achievement.id.asc()).all()
        user_unlocks = {
            pa.achievement_id: pa.unlocked_at
            for pa in db.session.query(PlayerAchievement).filter_by(user_id=user_id).all()
        }

        output = []
        for ach in all_achievements:
            is_unlocked = ach.id in user_unlocks
            unlocked_at = user_unlocks.get(ach.id)
            output.append({
                **ach.to_dict(),
                "is_unlocked": is_unlocked,
                "unlocked_at": unlocked_at.isoformat() if unlocked_at else None,
            })
        return output

    def unlock_achievement(self, user_id: int, achievement_id: int) -> bool:
        """Unlock an achievement and award its XP & Coin rewards idempotently."""
        existing = (
            db.session.query(PlayerAchievement)
            .filter_by(user_id=user_id, achievement_id=achievement_id)
            .first()
        )
        if existing:
            return False

        achievement = db.session.get(Achievement, achievement_id)
        if not achievement:
            return False

        pa = PlayerAchievement(user_id=user_id, achievement_id=achievement_id)
        db.session.add(pa)

        # Grant rewards
        stats = self.get_or_create_stats(user_id)
        stats.total_xp += achievement.xp_reward
        stats.coins += achievement.coin_reward
        stats.level = PlayerStatistics.calculate_level_from_xp(stats.total_xp)

        # Record ledgers
        db.session.add(
            XPTransaction(
                user_id=user_id,
                amount=achievement.xp_reward,
                source_type="achievement",
                reference_id=achievement.code,
                description=f"Unlocked: {achievement.title}",
            )
        )
        db.session.add(
            RewardTransaction(
                user_id=user_id,
                amount=achievement.coin_reward,
                currency_type="coins",
                source_type="achievement",
                reference_id=achievement.code,
                description=f"Unlocked: {achievement.title}",
            )
        )

        db.session.commit()
        return True
