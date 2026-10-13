"""
Production Gunicorn Configuration for Quiz Royale.
Tuned for high-concurrency competitive multiplayer gameplay, WebSocket upgrades,
worker recycling, and zero memory leaks.
"""

import os
import multiprocessing

# ================= Networking & Bindings =================
port = os.getenv("PORT", "5000")
host = os.getenv("HOST", "0.0.0.0")
bind = f"{host}:{port}"
backlog = 2048

# ================= Process & Thread Management =================
# Dynamic worker calculation with environmental overrides
cpu_count = multiprocessing.cpu_count()
default_workers = max(2, min(cpu_count * 2, 8))
workers = int(os.getenv("GUNICORN_WORKERS", default_workers))
threads = int(os.getenv("GUNICORN_THREADS", 4))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
worker_connections = 1000

# ================= Memory & Lifecycle Management =================
# Worker recycling to mitigate fragmentation and subtle C-level leaks
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 100))

# Timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", 60))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 30))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))

# ================= Logging & Diagnostics =================
loglevel = os.getenv("LOG_LEVEL", "info").lower()
accesslog = "-"
errorlog = "-"
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(L)ss "%(f)s" "%(a)s"'
)

# ================= Server Lifecycle Hooks =================
def on_starting(server):
    """Callback fired when Gunicorn master process initializes."""
    server.log.info("Starting Quiz Royale Production Engine...")
    server.log.info(f"Binding to {bind} with {workers} workers and {threads} threads/worker.")


def post_fork(server, worker):
    """Callback fired immediately after a worker process is spawned."""
    server.log.info(f"Worker spawned [pid={worker.pid}]")


def worker_int(worker):
    """Callback fired when worker receives SIGINT / SIGQUIT."""
    worker.log.info(f"Worker received termination signal [pid={worker.pid}]")
