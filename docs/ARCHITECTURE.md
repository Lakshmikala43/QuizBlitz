# Quiz Royale — System Architecture & Design Specification

## 1. System Overview
Quiz Royale is a modular full-stack competitive quiz gaming platform designed for high concurrency, deterministic game state execution, and engaging client-side interaction without external commercial dependencies.

```
+-----------------------------------------------------------------------------------+
|                              Client Browser Tier                                 |
|  - Semantic HTML5 & CSS3 Design System (Dark Charcoal / Deep Purple / Amber Gold) |
|  - Vanilla JavaScript ES Modules (State, Audio Synth, WebSocket, Form Handlers)   |
|  - Web Audio Synthesizer (Real-time dynamic game SFX, Zero audio file downloads)  |
+-----------------------------------------------------------------------------------+
                                        |  ^
                     HTTPS / JSON REST  |  |  WSS (Flask-SocketIO WebSockets)
                                        v  |
+-----------------------------------------------------------------------------------+
|                             Application Gateway / WSGI                            |
|                          (Flask Application Factory)                              |
+-----------------------------------------------------------------------------------+
        |                         |                         |               |
        v                         v                         v               v
+-----------------+      +-----------------+      +-----------------+  +------------+
| Auth & RBAC     |      | Game Engine     |      | Real-Time Battle|  | Admin & Ops|
| Blueprint       |      | Blueprint       |      | SocketIO Room   |  | Blueprint  |
| - Sessions      |      | - Solo / Survival|      | - Synced Ticks  |  | - Question |
| - CSRF Tokens   |      | - Time Attack   |      | - Anti-Cheat    |  |   CRUD     |
| - User Profile  |      | - Daily Quiz    |      | - Live Scores   |  | - Import   |
+-----------------+      +-----------------+      +-----------------+  +------------+
        |                         |                         |               |
        +-------------------------+-------------------------+---------------+
                                  |
                                  v
+-----------------------------------------------------------------------------------+
|                           Domain Service & Business Logic                         |
|  - Scoring Engine (Base + Latency Decay + Streak Multipliers)                     |
|  - Progression Service (XP, Levels: XP = 100 * level^1.5, Coins, Badges)         |
|  - Session Validator (Idempotent Submissions, Authoritative Answer Concealment)   |
|  - Multiplayer Room Orchestrator (State Machine: LOBBY -> COUNTDOWN -> ACTIVE)    |
+-----------------------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------------------+
|                        Repository Layer (Data Access Object)                      |
|  - BaseRepository, UserRepository, QuestionRepository, GameSessionRepository      |
|  - Decoupled from SQL dialect: Pure SQLAlchemy 2.0 ORM Query Expressions          |
+-----------------------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------------------+
|                            Persistence Tier (Database)                            |
|  - SQLite (Local zero-config development) / PostgreSQL (Production ready)         |
|  - 18+ Relational Tables, Foreign Keys, Unique Indexes, Check Constraints         |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Architectural Principles

### 2.1 Authoritative Server Model
- The frontend **never** receives correct answer keys or option correctness indicators until an answer has been authoritatively submitted or the server timer expires.
- Game timers are tracked by timestamp on the server session. If a client submits after the server-allotted window plus a 1.0-second network latency grace window, the submission is marked as expired.
- Duplicate submissions with the same idempotency key or on the same question index are safely rejected without awarding double score or corrupting statistics.

### 2.2 Client-Side Synthesizer Engine (Zero Assets)
Instead of relying on fragile audio asset links, Quiz Royale embeds a custom Web Audio API synthesizer directly in JavaScript:
- Generates 8-bit / modern polyphonic chimes for clicks, countdown ticks, correct answers, wrong buzzes, streaks, victory fanfares, and game over.
- Provides a persistent sound mute/unmute control saved in `localStorage`.
- Degrades gracefully if audio contexts are blocked by browser autoplay policies.

### 2.3 Real-Time Multiplayer Protocol
Multiplayer battles run over Flask-SocketIO using a synchronized state machine:
- **`create_room`**: Host initializes a 6-character room code, selecting category and difficulty.
- **`join_room`**: Peers join room and announce presence.
- **`player_ready`**: Host and peers toggle ready status.
- **`start_match`**: Host launches match once all players are ready.
- **`question_tick`**: Server broadcasts question text and options simultaneously to all room sockets with a uniform server timestamp.
- **`submit_answer`**: Players submit choices. Real-time scores and live standing indicators are pushed to all participants.
- **`match_complete`**: Server records match results in the database and broadcasts the final podium rankings.

### 2.4 Security & RBAC Boundaries
- Passwords are encrypted using Werkzeug PBKDF2/SHA256 modern password hashing.
- Role-based authorization via custom `@admin_required` decorators protects all management routes.
- Audit logging automatically records destructive administrator actions (question deletions, user bans, category modifications).
