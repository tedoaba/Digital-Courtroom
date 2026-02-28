# Use pinned python slim image
FROM python:3.12.9-slim AS base

# Install uv via pip (more robust than GHCR copy in some restricted networks)
RUN pip install --no-cache-dir uv

# Set environment variables
ENV PATH="${PATH}" \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN groupadd -r courtroom && useradd -r -g courtroom courtroom_user

# Create necessary directories and set permissions
RUN mkdir -p /app /audit /reports && \
    chown -R courtroom_user:courtroom /app /audit /reports && \
    chmod 755 /app /reports && \
    chmod 777 /audit

WORKDIR /app

# Install dependencies in a separate stage for caching
FROM base AS builder
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Final stage
FROM base
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY --chown=courtroom_user:courtroom . .

# Final sync to install the project itself (entrypoints)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Fix potential Windows CRLF line endings and ensure entrypoint is executable
RUN tr -d '\r' < scripts/docker-entrypoint.sh > scripts/docker-entrypoint.sh.tmp && \
    mv scripts/docker-entrypoint.sh.tmp scripts/docker-entrypoint.sh && \
    chmod +x scripts/docker-entrypoint.sh && \
    head -n 1 scripts/docker-entrypoint.sh | cat -e

# Use non-root user
USER courtroom_user

# Entrypoint
ENTRYPOINT ["/bin/bash", "/app/scripts/docker-entrypoint.sh"]
CMD ["courtroom"]
