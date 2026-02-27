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
RUN uv sync --frozen --no-dev --no-install-project

# Final stage
FROM base
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY . .

# Final sync to install the project itself (entrypoints)
RUN uv sync --frozen --no-dev

# Ensure entrypoint is executable
RUN chmod +x scripts/docker-entrypoint.sh

# Use non-root user
USER courtroom_user

# Entrypoint
ENTRYPOINT ["scripts/docker-entrypoint.sh"]
CMD ["courtroom"]
