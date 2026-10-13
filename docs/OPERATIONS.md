# Quiz Royale — Operations & Disaster Recovery Playbook

This document details ongoing operations, maintenance schedules, database backups, performance monitoring, and disaster recovery procedures for **Quiz Royale**.

---

## 1. Database Maintenance & Backup Schedules

### 1.1 PostgreSQL Production Backups

Set up automated daily backups with 30-day retention using `cron`:

```bash
# /etc/cron.daily/quizroyale-backup
#!/bin/bash
BACKUP_DIR="/var/backups/quizroyale"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

pg_dump -U quizroyale -h localhost -d quizroyale_prod -Fc -f "$BACKUP_DIR/quizroyale_$TIMESTAMP.dump"
gzip -t "$BACKUP_DIR/quizroyale_$TIMESTAMP.dump"

# Delete backups older than 30 days
find "$BACKUP_DIR" -type f -name "quizroyale_*.dump" -mtime +30 -delete
```

### 1.2 PostgreSQL Point-In-Time Restore (Disaster Recovery)

```bash
# 1. Terminate active application traffic
sudo systemctl stop quizroyale

# 2. Drop existing broken database
sudo -u postgres dropdb quizroyale_prod

# 3. Re-create empty target database
sudo -u postgres createdb -O quizroyale quizroyale_prod

# 4. Restore from latest verified dump
pg_restore -U quizroyale -d quizroyale_prod -v /var/backups/quizroyale/quizroyale_latest.dump

# 5. Restart application
sudo systemctl start quizroyale
```

### 1.3 SQLite Local Development Maintenance (WAL Mode)

When running in SQLite mode:
- **Write-Ahead Logging (WAL)**: Enabled by default to prevent reader-writer lock contention.
- **WAL Checkpointing**:
  ```python
  import sqlite3
  conn = sqlite3.connect("instance/quizroyale.db")
  conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
  conn.close()
  ```
- **Database Vacuum**: Run monthly during low-traffic windows:
  ```bash
  sqlite3 instance/quizroyale.db "VACUUM;"
  ```

---

## 2. Health Monitoring & Observability

### 2.1 Synthetic Liveness & Diagnostics Endpoints

Quiz Royale provides dedicated health probes:
- **Liveness Probe**: `GET /api/v1/health`
  - Returns HTTP 200 with JSON payload when the application process is responsive.
- **Diagnostics Probe**: `GET /api/v1/status`
  - Returns runtime telemetry, active feature flags, database connection health, and Python engine version.

### 2.2 Systemd Journal Inspection

```bash
# Tail live application log stream
journalctl -u quizroyale -f

# Filter error logs from the past 24 hours
journalctl -u quizroyale --since "24 hours ago" -p err
```

### 2.3 Gunicorn Worker Telemetry

Inspect response times and upstream latency logged by Gunicorn:
```bash
tail -f /var/log/quizroyale/access.log | awk '{print $1, $7, $9, $10}'
```

---

## 3. Rate Limiting & Security Safeguards

- **Application-Level Sliding Window Limiter**: Configured on `/login`, `/register`, and `/api/v1/auth/*` routes.
- **Nginx Connection Capping**:
  ```nginx
  limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s;
  limit_req zone=api_limit burst=50 nodelay;
  ```
- **CSRF Token Validation**: Enforced across all HTML form submissions. REST API v1 endpoints under `/api/v1` use session token headers or stateless request verification.

---

## 4. Question Bank Management & Moderation

- **Question Reports Resolution**: Administrators review player-flagged questions via `/admin/reports`.
- **Editorial Publishing**: Questions can be drafted and kept unpublished until reviewed by subject matter experts.
- **Audit Logs**: Every administrative change (user suspension, role alteration, category creation) is permanently appended to the immutable `audit_logs` table.
