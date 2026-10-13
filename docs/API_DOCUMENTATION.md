# Quiz Royale — REST API v1 Reference & Developer Guide

The Quiz Royale REST API exposes full programmatic control over player accounts, quiz matchmaking, live gameplay sessions, leaderboard analytics, and administrative auditing.

---

## 1. Architecture & Conventions

### Base URL
```http
http://localhost:5000/api/v1
```

### Standard Response Envelope

#### Successful Response (`200 OK`, `201 Created`)
```json
{
  "status": "success",
  "message": "Session started successfully.",
  "data": { ... },
  "meta": {
    "page": 1,
    "total": 48
  }
}
```

#### Error Response (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `422 Unprocessable`)
```json
{
  "status": "error",
  "code": 401,
  "error_code": "UNAUTHORIZED",
  "message": "Authentication required to access this endpoint."
}
```

---

## 2. Authentication & Sessions

Quiz Royale supports secure cookie-based session authentication. Programmatic API clients initiate a session by calling `/api/v1/auth/login`.

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new warrior account | No |
| `POST` | `/api/v1/auth/login` | Log in and receive session cookie | No |
| `POST` | `/api/v1/auth/logout` | Invalidate current session | Yes |
| `GET` | `/api/v1/auth/me` | Fetch authenticated player profile & stats | Yes |

---

## 3. Categories & Question Catalog

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/categories` | List all 14 active categories with question totals | No |
| `GET` | `/api/v1/categories/<slug>` | Get category details with difficulty breakdown | No |
| `GET` | `/api/v1/questions/sample` | Anti-cheat scrubbed questions for practice | No |
| `GET` | `/api/v1/questions/<id>` | Fetch single question (safe for players, full for admin) | No |
| `GET` | `/api/v1/questions` | Administrative bank search & filter | Admin |

---

## 4. Authoritative Gameplay Engine

The gameplay engine is 100% server-authoritative. The client receives one scrubbed question at a time. The server validates response timestamps, awards speed bonus points, computes streak multipliers, and updates persistent XP and coins.

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/games/start` | Launch a game session (`solo`, `time_attack`, `survival`, `practice`) | Yes |
| `GET` | `/api/v1/games/<session_id>/question` | Fetch current active question | Yes |
| `POST` | `/api/v1/games/<session_id>/submit` | Submit answer with idempotency support | Yes |
| `GET` | `/api/v1/games/<session_id>/summary` | Fetch final score, accuracy, and rewards | Yes |

---

## 5. Leaderboards & Player Stats

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/leaderboards` | Query ranked rankings (`all_time`, `daily`, `weekly`) | No |
| `GET` | `/api/v1/players/<username>` | Public warrior profile card, level, and unlocked trophies | No |
| `GET` | `/api/v1/players/<username>/history` | Paginated match history | No |
| `GET` | `/api/v1/achievements` | Platform badges & achievement criteria | No |

---

## 6. Real-Time Multiplayer Rooms

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/multiplayer/rooms` | Discover active open room lobbies | No |
| `POST` | `/api/v1/multiplayer/rooms` | Create a room lobby | Yes |
| `GET` | `/api/v1/multiplayer/rooms/<code>` | Get room state, participants, and status | No |

---

## 7. Administrative Telemetry

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/admin/overview` | Platform health metrics & operational numbers | Admin |
| `GET` | `/api/v1/admin/users` | User directory search with status filters | Admin |
| `GET` | `/api/v1/admin/audit-logs` | Immutable audit trail of administrative actions | Admin |
