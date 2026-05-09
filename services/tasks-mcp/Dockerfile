# =============================================================================
# Tasks MCP Server Dockerfile
# =============================================================================
# Purpose: Production-ready container for Tasks MCP Server
# Features: Multi-stage build, slim base, non-root user, UV package manager
# Usage: docker build -t tasks-mcp:v1 . && docker run -p 8000:8000 tasks-mcp:v1
# =============================================================================


# =============================================================================
# STAGE 1: Builder
# =============================================================================
# Purpose: Install dependencies in isolated environment
# Using slim variant for better compatibility with MCP dependencies
# =============================================================================
FROM python:3.12-slim AS builder

# -----------------------------------------------------------------------------
# Install UV Package Manager (10-100x faster than pip)
# -----------------------------------------------------------------------------
# Copy from official UV image - no need to install curl/wget
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# -----------------------------------------------------------------------------
# Copy Dependency Files ONLY (Cache Optimization)
# -----------------------------------------------------------------------------
# Dependencies change less frequently than code
# This layer is cached until pyproject.toml or uv.lock changes
# README.md needed by hatchling build backend (referenced in pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

# -----------------------------------------------------------------------------
# Install Dependencies Only (not the project itself)
# -----------------------------------------------------------------------------
# --frozen: Use exact lockfile versions (reproducible builds)
# --no-dev: Exclude development dependencies (pytest, etc.)
# --no-install-project: Install deps only, not the project (source not ready yet)
RUN uv sync --frozen --no-dev --no-install-project

# -----------------------------------------------------------------------------
# Copy Source Code and Install Project
# -----------------------------------------------------------------------------
COPY src/ ./src/
RUN uv sync --frozen --no-dev


# =============================================================================
# STAGE 2: Runtime
# =============================================================================
# Purpose: Minimal production image
# Contains: Only Python runtime + dependencies + application code
# Excludes: Build tools, dev dependencies, UV binary
# =============================================================================
FROM python:3.12-slim

# -----------------------------------------------------------------------------
# Create Non-Root User (Security Best Practice)
# -----------------------------------------------------------------------------
# Never run production containers as root
# Limits damage if container is compromised
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# -----------------------------------------------------------------------------
# Copy Virtual Environment from Builder Stage
# -----------------------------------------------------------------------------
# Only the .venv is needed, not build tools
# This is why multi-stage builds produce smaller images
COPY --from=builder /app/.venv /app/.venv

# -----------------------------------------------------------------------------
# Copy Application Source Code
# -----------------------------------------------------------------------------
# --chown: Set ownership to non-root user
# Copied LAST for optimal layer caching
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser pyproject.toml ./

# -----------------------------------------------------------------------------
# Set Environment Variables
# -----------------------------------------------------------------------------
# PATH: Add venv bin to path so we can run installed commands
# PYTHONUNBUFFERED: Send output directly to terminal (better logging)
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# -----------------------------------------------------------------------------
# Switch to Non-Root User
# -----------------------------------------------------------------------------
# All subsequent commands and container runtime use this user
USER appuser

# -----------------------------------------------------------------------------
# Document Port (Metadata Only)
# -----------------------------------------------------------------------------
# EXPOSE is documentation; actual port publishing via: docker run -p 8000:8000
# FastMCP streamable-http default port is 8000
EXPOSE 8000

# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------
# MCP uses SSE protocol, so standard HTTP GET returns 406 (expected)
# We check if server responds at all (any status means server is alive)
# --interval: Check every 30 seconds
# --timeout: Fail if check takes longer than 10 seconds
# --start-period: Grace period for app startup
# --retries: Mark unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; import urllib.error; \
        try: urllib.request.urlopen('http://localhost:8000/mcp'); \
        except urllib.error.HTTPError: pass" || exit 1

# -----------------------------------------------------------------------------
# Container Startup Command
# -----------------------------------------------------------------------------
# Run the MCP server using the installed entry point
# EXEC form ["cmd"] for proper signal handling (SIGTERM)
CMD ["python", "-m", "tasks_mcp.server"]
