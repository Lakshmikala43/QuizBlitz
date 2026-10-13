# Multi-stage production Dockerfile for Quiz Royale Platform
# Optimized for minimum image footprint, zero root execution, and high security.

# ================= Stage 1: Build Dependencies =================
FROM python:3.13-slim AS builder

WORKDIR /build

# Install build dependencies for C-extensions if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Compile wheels into wheelhouse
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir=/build/wheels -r requirements.txt gunicorn


# ================= Stage 2: Runtime Container =================
FROM python:3.13-slim AS runtime

# Label metadata
LABEL maintainer="Quiz Royale Engineering Team"
LABEL version="1.0.0"
LABEL description="Production-grade Full-Stack Quiz Gaming Platform"

# Hardened environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=wsgi.py \
    PORT=5000 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# Install minimal runtime utilities (curl for healthcheck, sqlite3)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from builder
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && \
    rm -rf /wheels

# Create dedicated non-root application user
RUN groupadd -g 10001 quizroyale && \
    useradd -u 10001 -g quizroyale -s /sbin/nologin -d ${APP_HOME} quizroyale

# Copy application source code
COPY --chown=quizroyale:quizroyale . ${APP_HOME}

# Create persistent instance directory for SQLite databases and seed logs
RUN mkdir -p ${APP_HOME}/instance ${APP_HOME}/logs && \
    chown -R quizroyale:quizroyale ${APP_HOME}/instance ${APP_HOME}/logs

# Switch to unprivileged execution user
USER quizroyale

# Expose standard service port
EXPOSE 5000

# Container healthcheck hitting engine liveness probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# Default runtime entrypoint
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
