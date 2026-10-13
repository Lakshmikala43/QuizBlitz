# Quiz Royale — Full-Stack Competitive Quiz Gaming Platform

Quiz Royale is an enterprise-grade, full-stack multiplayer competitive quiz gaming platform built using Python 3, Flask, Flask-SocketIO, SQLite/PostgreSQL-ready SQLAlchemy ORM, and vanilla HTML5, CSS3, and modern JavaScript.

Designed with a gaming visual aesthetic (deep purples, dark charcoals, warm amber/coral accents), rich interactive audio synthesized client-side with zero external audio assets, and a strictly authoritative game engine preventing client-side score manipulation.

---

## Key Highlights

- **Zero Mandatory External API Keys**: 100% self-contained question banks, deterministic game sessions, local avatar generators, and Web Audio synthesizer.
- **Authoritative Server Engine**: Server-calculated timing, streak multipliers, speed bonus curves, and idempotent submissions.
- **6 Rich Game Modes**:
  1. *Solo Classic* (Custom categories, difficulty, question volume)
  2. *Time Attack* (Answer maximum questions before timer expires)
  3. *Survival Mode* (3 strikes and game over)
  4. *Daily Challenge* (Deterministic daily quiz, 1 ranked entry per day)
  5. *Practice Mode* (Untimed, immediate explanations, retries)
  6. *Multiplayer Battle* (Real-time synchronized lobbies with Flask-SocketIO)
- **14 Comprehensive Categories**: Python, Java, C/C++, Data Structures & Algorithms, DBMS & SQL, Operating Systems, Computer Networks, Cybersecurity, Mathematics, Logical Reasoning, General Knowledge, Science, Sports, Movies & Entertainment.
- **25 Dedicated Pages & Views**: Including player dashboards, analytics, leaderboards, achievements, moderation, audit trails, and administration tools.
- **Full Administrative Control**: Question CRUD, category management, bulk CSV/JSON import, report moderation, audit logs, and user status toggling.
- **Strict Verification & Testing**: pytest unit, integration, security, and socket tests.

---

## Quickstart Guide

### 1. Requirements
- Python 3.11+
- Git

### 2. Installation
```bash
# Clone or navigate to the repository
cd quiz-royale

# Set up virtual environment (optional)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
python scripts/seed_database.py
```

### 4. Run Application
```bash
python run.py
```
Open your browser at `http://127.0.0.1:5000`.

Default administrator credentials (created by seeder):
- **Username**: `admin`
- **Password**: `AdminRoyale2026!`

Default test player credentials:
- **Username**: `player1`
- **Password**: `PlayerRoyale2026!`

---

## Testing & Quality Assurance
```bash
# Run pytest test suite
pytest

# Measure codebase lines of code
python scripts/measure_loc.py
```

---

## Architecture Overview
See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) for architectural blueprints, ER diagrams, and sequence flows.
