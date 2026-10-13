from typing import Tuple, Dict

DIFFICULTY_BASE_POINTS = {
    "easy": 100,
    "medium": 200,
    "hard": 300,
}

MAX_STREAK_CAP = 5
MAX_SPEED_BONUS = 50


class ScoringEngine:
    """Authoritative server-side scoring calculator."""

    @staticmethod
    def calculate_submission_score(
        difficulty: str,
        is_correct: bool,
        response_time_ms: int,
        time_limit_sec: int,
        current_streak: int,
    ) -> Tuple[int, int, int, int]:
        """
        Compute authoritative points for a question submission.
        Returns: (points_awarded, streak_bonus, speed_bonus, new_streak)
        """
        if not is_correct:
            return 0, 0, 0, 0

        # 1. Base Points
        base = DIFFICULTY_BASE_POINTS.get(difficulty.lower(), 100)

        # 2. Streak Multiplier
        # Consecutive streak adds 10% per streak up to 50% max bonus
        new_streak = current_streak + 1
        effective_streak = min(new_streak, MAX_STREAK_CAP)
        streak_multiplier = 1.0 + (max(0, effective_streak - 1) * 0.10)
        streak_points = int(base * (streak_multiplier - 1.0))

        # 3. Speed Bonus
        # Faster answers receive up to 50 extra points
        time_limit_ms = max(5000, time_limit_sec * 1000)
        speed_bonus = 0
        if response_time_ms < (time_limit_ms * 0.75):
            fraction_remaining = 1.0 - (response_time_ms / (time_limit_ms * 0.75))
            speed_bonus = max(0, min(MAX_SPEED_BONUS, int(MAX_SPEED_BONUS * fraction_remaining)))

        total_awarded = base + streak_points + speed_bonus
        return total_awarded, streak_points, speed_bonus, new_streak

    @staticmethod
    def calculate_match_rewards(
        total_score: int,
        accuracy_pct: float,
        game_mode: str,
        best_streak: int,
    ) -> Tuple[int, int]:
        """
        Calculate final XP and Coin rewards upon match completion.
        Returns: (xp_earned, coins_earned)
        """
        if game_mode == "practice":
            # Practice mode is untimed/unranked with nominal reward
            return 10, 2

        # Base XP scaled from score + accuracy bonus
        base_xp = int(total_score * 0.20)
        accuracy_bonus = int(accuracy_pct * 1.5)
        streak_xp = best_streak * 10
        total_xp = max(25, base_xp + accuracy_bonus + streak_xp)

        # Coins awarded based on score and high accuracy
        base_coins = int(total_score * 0.04)
        accuracy_coins = 15 if accuracy_pct >= 80.0 else (5 if accuracy_pct >= 50.0 else 0)
        total_coins = max(5, base_coins + accuracy_coins)

        return total_xp, total_coins
