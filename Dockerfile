# ───────────────────────────────────────────────────────────────────────────────
# Multi-Stage Dockerfile — Day 29: Production Optimization
#
# Stage 1 (builder): installs dependencies into a virtual environment
# Stage 2 (runtime): copies only the venv and application code
#
# Benefits vs. single-stage:
#   • No build tools (gcc, pip, wheel caches) in the final image
#   • python:3.11-slim base ≈ 60 MB vs. python:3.9 full ≈ 330 MB
#   • Deterministic, reproducible builds
# ───────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Dependency Builder ────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install OS build dependencies (only needed for compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first so Docker layer caching works
COPY requirements.txt .

# Create a venv and install all dependencies into it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Production Runtime ────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Install only runtime OS dependencies (no compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security hardening
RUN groupadd --gid 1001 appgroup && \
    useradd  --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

WORKDIR /app

# Copy the pre-built virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source (excludes paths in .dockerignore)
COPY --chown=appuser:appgroup . .

# Activate venv for all subsequent commands
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_FORMAT=json \
    LOG_LEVEL=INFO

# Drop to non-root
USER appuser

EXPOSE 8000

# Health check — Docker will mark the container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl --fail --silent http://localhost:8000/health || exit 1

# Production Uvicorn: multiple workers, structured access logs
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--access-log", \
     "--log-level", "info"]
