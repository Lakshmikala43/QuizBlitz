import pytest
from app.games.scoring import ScoringEngine, DIFFICULTY_BASE_POINTS, MAX_STREAK_CAP, MAX_SPEED_BONUS


class TestScoringEngine:
    """Unit test suite for authoritative scoring algorithms and progression curves."""

    def test_incorrect_answer_yields_zero_and_resets_streak(self):
        total, streak_pts, speed_pts, new_streak = ScoringEngine.calculate_submission_score(
            difficulty="hard",
            is_correct=False,
            response_time_ms=1200,
            time_limit_sec=15,
            current_streak=4,
        )
        assert total == 0
        assert streak_pts == 0
        assert speed_pts == 0
        assert new_streak == 0

    def test_base_points_by_difficulty(self):
        # When streak is 0 and response is slow (no speed bonus)
        for diff, expected_base in [("easy", 100), ("medium", 200), ("hard", 300)]:
            total, streak_pts, speed_pts, new_streak = ScoringEngine.calculate_submission_score(
                difficulty=diff,
                is_correct=True,
                response_time_ms=14000,
                time_limit_sec=15,
                current_streak=0,
            )
            assert total == expected_base
            assert streak_pts == 0
            assert speed_pts == 0
            assert new_streak == 1

    def test_streak_multiplier_scaling_and_capping(self):
        # 1st correct answer -> streak becomes 1 (no multiplier bonus)
        _, streak_pts_1, _, s1 = ScoringEngine.calculate_submission_score("easy", True, 14000, 15, 0)
        assert s1 == 1
        assert streak_pts_1 == 0

        # 2nd correct answer -> streak becomes 2 (10% bonus)
        _, streak_pts_2, _, s2 = ScoringEngine.calculate_submission_score("easy", True, 14000, 15, 1)
        assert s2 == 2
        assert streak_pts_2 == 10  # 10% of 100

        # 5th correct answer -> streak becomes 5 (40% bonus)
        _, streak_pts_5, _, s5 = ScoringEngine.calculate_submission_score("easy", True, 14000, 15, 4)
        assert s5 == 5
        assert streak_pts_5 == 40  # 40% of 100

        # 10th correct answer -> capped at MAX_STREAK_CAP (5 -> 40% bonus)
        _, streak_pts_10, _, s10 = ScoringEngine.calculate_submission_score("easy", True, 14000, 15, 9)
        assert s10 == 10
        assert streak_pts_10 == 40

    def test_speed_bonus_decay_curve(self):
        # Instant answer (100ms) gets maximum speed bonus (~50 pts)
        _, _, speed_fast, _ = ScoringEngine.calculate_submission_score("medium", True, 100, 15, 0)
        assert speed_fast == MAX_SPEED_BONUS

        # Halfway into speed window
        _, _, speed_mid, _ = ScoringEngine.calculate_submission_score("medium", True, 5000, 15, 0)
        assert 10 < speed_mid < MAX_SPEED_BONUS

        # Past the speed bonus window (>= 75% of time limit)
        _, _, speed_slow, _ = ScoringEngine.calculate_submission_score("medium", True, 12000, 15, 0)
        assert speed_slow == 0

    def test_match_rewards_practice_vs_ranked(self):
        # Practice mode returns minimal flat rewards
        xp_prac, coins_prac = ScoringEngine.calculate_match_rewards(
            total_score=1500, accuracy_pct=100.0, game_mode="practice", best_streak=5
        )
        assert xp_prac == 10
        assert coins_prac == 2

        # Ranked mode scales with score, accuracy, and streak
        xp_ranked, coins_ranked = ScoringEngine.calculate_match_rewards(
            total_score=1000, accuracy_pct=80.0, game_mode="solo", best_streak=4
        )
        # Base XP: 1000 * 0.20 = 200, accuracy bonus: 80 * 1.5 = 120, streak: 40 -> 360 XP
        assert xp_ranked >= 350
        assert coins_ranked >= 20
