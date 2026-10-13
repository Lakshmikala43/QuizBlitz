# Quiz Royale — Database Schema & Data Dictionary

Quiz Royale utilizes a normalized relational database schema with full support for SQLite in local development and PostgreSQL in production.

```
                           +-------------------+
                           |       users       |
                           +-------------------+
                             |     |       |
                 +-----------+     |       +-----------+
                 |                 |                   |
                 v                 v                   v
        +-----------------+ +----------------+ +------------------+
        |   user_roles    | | player_stats   | | player_achieve   |
        +-----------------+ +----------------+ +------------------+
                 ^                                     ^
                 |                                     |
        +-----------------+                   +------------------+
        |      roles      |                   |   achievements   |
        +-----------------+                   +------------------+
                 |
                 +-------------------+
                 |                   |
                 v                   v
        +-----------------+ +----------------+
        |   xp_txns       | | reward_txns    |
        +-----------------+ +----------------+

        +-----------------+
        |   categories    |
        +-----------------+
                 |
                 v
        +-----------------+          +---------------------+
        |    questions    | <------- |  daily_challenges   |
        +-----------------+          +---------------------+
                 |                              |
                 v                              v
        +-----------------+          +---------------------+
        |  answer_options |          | daily_chall_attempts|
        +-----------------+          +---------------------+

                 |                              |
                 v                              v
        +-----------------+          +---------------------+
        |  quiz_sessions  | -------> |    match_results    |
        +-----------------+          +---------------------+
           |            |
           v            v
    +-------------+ +--------------------+
    | session_qs  | | answer_submissions |
    +-------------+ +--------------------+

        +-------------------+        +---------------------+
        | multiplayer_rooms | -----> |  room_participants  |
        +-------------------+        +---------------------+

        +-------------------+        +---------------------+
        |     reports       |        |     audit_logs      |
        +-------------------+        +---------------------+
```

---

## Entity Data Dictionary

### 1. `users`
- `id` (Integer, Primary Key, Auto-increment)
- `username` (String(64), Unique, Indexed, Not Null)
- `email` (String(120), Unique, Indexed, Not Null)
- `password_hash` (String(256), Not Null)
- `display_name` (String(64), Nullable)
- `avatar_seed` (String(64), Default 'default')
- `bio` (String(256), Nullable)
- `is_active` (Boolean, Default True)
- `is_admin` (Boolean, Default False)
- `reset_token` (String(100), Nullable)
- `reset_token_expiry` (DateTime, Nullable)
- `last_login_at` (DateTime, Nullable)
- `created_at` (DateTime, Default UTC now)
- `updated_at` (DateTime, Default UTC now)

### 2. `roles` & `user_roles`
- `roles`: `id`, `name` (Unique: 'player', 'moderator', 'admin'), `description`
- `user_roles`: `id`, `user_id` (FK users.id), `role_id` (FK roles.id), `assigned_at`

### 3. `categories`
- `id` (Integer, Primary Key)
- `name` (String(64), Unique, Not Null)
- `slug` (String(64), Unique, Not Null)
- `description` (Text, Nullable)
- `icon` (String(32), Default 'fa-gamepad')
- `color_hex` (String(16), Default '#6366f1')
- `is_active` (Boolean, Default True)
- `sort_order` (Integer, Default 0)
- `created_at` (DateTime)

### 4. `questions`
- `id` (Integer, Primary Key)
- `category_id` (Integer, FK categories.id, Indexed, Not Null)
- `question_text` (Text, Not Null)
- `difficulty` (String(16), Enum: 'easy', 'medium', 'hard', Not Null)
- `explanation` (Text, Nullable)
- `time_limit_sec` (Integer, Default 15)
- `points` (Integer, Default 100)
- `is_published` (Boolean, Default True)
- `author_id` (Integer, FK users.id, Nullable)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### 5. `answer_options`
- `id` (Integer, Primary Key)
- `question_id` (Integer, FK questions.id, Indexed, Not Null)
- `option_text` (Text, Not Null)
- `is_correct` (Boolean, Default False, Not Null)
- `order_index` (Integer, Default 0)

### 6. `quiz_sessions`
- `id` (String(36), UUID Primary Key)
- `user_id` (Integer, FK users.id, Indexed, Not Null)
- `category_id` (Integer, FK categories.id, Nullable for mixed/daily)
- `game_mode` (String(24), Enum: 'solo', 'time_attack', 'survival', 'daily', 'practice', 'multiplayer')
- `difficulty` (String(16), Default 'mixed')
- `total_questions` (Integer, Default 10)
- `current_question_index` (Integer, Default 0)
- `current_score` (Integer, Default 0)
- `current_streak` (Integer, Default 0)
- `best_streak` (Integer, Default 0)
- `lives_remaining` (Integer, Default 3 for Survival)
- `status` (String(24), Enum: 'created', 'in_progress', 'completed', 'abandoned', 'expired')
- `started_at` (DateTime)
- `completed_at` (DateTime, Nullable)

### 7. `session_questions`
- `id` (Integer, Primary Key)
- `session_id` (String(36), FK quiz_sessions.id, Indexed, Not Null)
- `question_id` (Integer, FK questions.id, Not Null)
- `question_order` (Integer, Not Null)
- `displayed_at` (DateTime, Nullable)

### 8. `answer_submissions`
- `id` (Integer, Primary Key)
- `session_id` (String(36), FK quiz_sessions.id, Indexed, Not Null)
- `question_id` (Integer, FK questions.id, Not Null)
- `selected_option_id` (Integer, FK answer_options.id, Nullable if timeout)
- `is_correct` (Boolean, Not Null)
- `response_time_ms` (Integer, Not Null)
- `points_awarded` (Integer, Default 0)
- `streak_bonus` (Integer, Default 0)
- `speed_bonus` (Integer, Default 0)
- `idempotency_key` (String(64), Nullable)
- `submitted_at` (DateTime)

### 9. `match_results`
- `id` (Integer, Primary Key)
- `session_id` (String(36), FK quiz_sessions.id, Unique, Not Null)
- `user_id` (Integer, FK users.id, Indexed, Not Null)
- `game_mode` (String(24), Not Null)
- `total_score` (Integer, Not Null)
- `correct_answers` (Integer, Not Null)
- `total_questions` (Integer, Not Null)
- `accuracy_pct` (Float, Not Null)
- `best_streak` (Integer, Not Null)
- `total_time_ms` (Integer, Not Null)
- `xp_earned` (Integer, Default 0)
- `coins_earned` (Integer, Default 0)
- `recorded_at` (DateTime)

### 10. `player_statistics`
- `id` (Integer, Primary Key)
- `user_id` (Integer, FK users.id, Unique, Indexed, Not Null)
- `total_xp` (Integer, Default 0)
- `level` (Integer, Default 1)
- `coins` (Integer, Default 0)
- `total_matches` (Integer, Default 0)
- `wins` (Integer, Default 0)
- `total_correct` (Integer, Default 0)
- `total_answered` (Integer, Default 0)
- `highest_score` (Integer, Default 0)
- `highest_streak` (Integer, Default 0)
- `daily_streak` (Integer, Default 0)
- `last_active_date` (Date, Nullable)

### 11. `achievements` & `player_achievements`
- `achievements`: `id`, `code` (Unique), `title`, `description`, `icon`, `xp_reward`, `coin_reward`, `tier` ('bronze', 'silver', 'gold', 'platinum')
- `player_achievements`: `id`, `user_id` (FK users.id), `achievement_id` (FK achievements.id), `unlocked_at`

### 12. `xp_transactions` & `reward_transactions`
- Ledger for auditing every point and coin awarded to prevent double-crediting.

### 13. `daily_challenges` & `daily_challenge_attempts`
- Deterministic daily challenges generated by date string (`YYYY-MM-DD`).

### 14. `multiplayer_rooms` & `room_participants`
- Multiplayer state tracking room codes, host, status ('lobby', 'in_progress', 'finished'), max players.

### 15. `reports`, `notifications`, `audit_logs`
- Moderation, user feedback, and security tracking entities.
