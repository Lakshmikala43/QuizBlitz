# Quiz Royale — Production Deployment Guide

This document provides exhaustive, step-by-step instructions for deploying **Quiz Royale** into production environments.

---

## 1. Architectural Overview

```
                      +-----------------------------+
                      |       Clients / Web         |
                      +--------------+--------------+
                                     |
                                     v
                        [ HTTPS / WSS: Port 443 ]
                                     |
                      +--------------v--------------+
                      |         Nginx 1.25+         |
                      |   - Static Asset Caching    |
                      |   - WebSocket Upgrade Handlers |
                      |   - SSL / TLS Termination   |
                      +--------------+--------------+
                                     |
                                     v
                          [ HTTP: Port 5000 ]
                                     |
                      +--------------v--------------+
                      |        Gunicorn WSGI        |
                      |  - Worker Pool (gthread)    |
                      |  - Event Loop (SocketIO)    |
                      |  - Signal Recycling         |
                      +--------------+--------------+
                                     |
                                     v
                      +--------------v--------------+
                      |    Quiz Royale Application  |
                      |   - Auth & Session Service  |
                      |   - Authoritative Game Eng  |
                      |   - REST API v1 Suite       |
                      +--------------+--------------+
                                     |
                      +--------------+--------------+
                      |                             |
                      v                             v
           +--------------------+         +--------------------+
           |  PostgreSQL 16     |         |  Local SQLite WAL  |
           |  (Production DB)   |         |  (Dev / Staging)   |
           +--------------------+         +--------------------+
```

---

## 2. Mandatory Zero-API-Key Guarantee

Quiz Royale was engineered from day one to operate completely autonomously with **strictly zero mandatory external API keys or cloud service accounts**:
- **Question Bank**: 100% locally seeded relational database tables.
- **Audio Effects**: Synthesized in real-time in the browser via the Web Audio API without downloading external audio files.
- **Avatar System**: Generated locally using deterministic SVG seed algorithms.
- **Authentication**: Modern scrypt password hashing with local session cookies.
- **Password Recovery**: Secure local development and offline cryptographic token exchange.

---

## 3. Environment Variables Reference

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | String | `production` | Runtime mode: `production`, `development`, or `testing`. |
| `SECRET_KEY` | String | *Required* | High-entropy cryptographic key for signing sessions and CSRF tokens. |
| `DATABASE_URL` | String | `sqlite:///instance/quizroyale.db` | SQLAlchemy connection URI. Supports PostgreSQL or SQLite. |
| `PORT` | Integer | `5000` | Network port for Gunicorn / Flask. |
| `HOST` | String | `0.0.0.0` | Network binding interface. |
| `GUNICORN_WORKERS` | Integer | `CPU * 2` | Number of worker processes in the Gunicorn pool. |
| `GUNICORN_THREADS` | Integer | `4` | Threads per worker process for concurrent connection handling. |
| `SOCKETIO_ASYNC_MODE` | String | `threading` | Asynchronous worker mode (`threading`, `eventlet`, `gevent`). |
| `LOG_LEVEL` | String | `info` | Logging verbosity (`debug`, `info`, `warning`, `error`). |

---

## 4. Containerized Deployment (Docker Compose)

### Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.20+

### Step-by-Step Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/example/quiz-royale.git
   cd quiz-royale
   ```

2. **Configure Environment Secrets**:
   Create a `.env` file in the project root:
   ```env
   FLASK_ENV=production
   SECRET_KEY=generate_with_python_secrets_token_hex_64
   DATABASE_URL=postgresql://quizroyale:quizroyale_prod_pass@db:5432/quizroyale_prod
   GUNICORN_WORKERS=4
   GUNICORN_THREADS=4
   ```

3. **Launch the Container Stack**:
   ```bash
   docker compose up -d --build
   ```

4. **Verify Container Health**:
   ```bash
   docker compose ps
   ```
   All containers (`quizroyale_web`, `quizroyale_db`, `quizroyale_nginx`) must report `healthy` or `running`.

5. **Seed Production Categories and Questions**:
   ```bash
   docker compose exec web python scripts/seed_database.py
   ```

6. **Inspect Engine Health**:
   ```bash
   curl http://localhost/api/v1/health
   ```
   Expected response:
   ```json
   {
     "status": "success",
     "message": "System operational",
     "data": {
       "status": "healthy",
       "service": "Quiz Royale Gameplay Engine",
       "version": "1.0.0"
     }
   }
   ```

---

## 5. Bare-Metal Linux Deployment (Ubuntu 22.04 / 24.04 LTS)

### 1. System Package Installation
```bash
sudo apt update && sudo apt install -y \
    python3.13 python3.13-venv python3.13-dev \
    postgresql postgresql-contrib \
    nginx curl git build-essential
```

### 2. Configure Dedicated Service User
```bash
sudo useradd -m -s /bin/bash -d /opt/quizroyale quizroyale
sudo su - quizroyale
git clone https://github.com/example/quiz-royale.git app
cd app
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn psycopg2-binary
exit
```

### 3. Configure PostgreSQL Database
```bash
sudo -u postgres psql -c "CREATE USER quizroyale WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE quizroyale_prod OWNER quizroyale;"
```

### 4. Create Systemd Service Unit (`/etc/systemd/system/quizroyale.service`)
```ini
[Unit]
Description=Quiz Royale Competitive Gaming Engine
After=network.target postgresql.service

[Service]
User=quizroyale
Group=quizroyale
WorkingDirectory=/opt/quizroyale/app
Environment="PATH=/opt/quizroyale/app/.venv/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your_production_secret_key"
Environment="DATABASE_URL=postgresql://quizroyale:your_secure_password@localhost:5432/quizroyale_prod"
ExecStart=/opt/quizroyale/app/.venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now quizroyale
sudo systemctl status quizroyale
```

### 5. Configure Nginx Reverse Proxy
Copy the provided `nginx/nginx.conf` into `/etc/nginx/sites-available/quizroyale`, enable the site, and obtain an SSL certificate via Certbot:
```bash
sudo ln -s /etc/nginx/sites-available/quizroyale /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d quizroyale.yourdomain.com
```

---

## 6. Verification and Smoke Testing

Run the automated test suite against the target installation:
```bash
pytest tests/ -v
```
All unit, integration, multiplayer, REST API, and end-to-end tests must pass without regressions.
