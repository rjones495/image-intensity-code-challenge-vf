FROM python:3.15-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /uvx /bin/

# Configure uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
ENV PYTHONUNBUFFERED=1

# Copy dependency configuration first for Docker layer caching
COPY pyproject.toml uv.lock README.md ./

# Install production dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY src/ ./src/

# Install the project
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Start the API
CMD ["uv", "run", "--no-sync", "uvicorn", "rob_jones_code_assessment.microservice.main:app", "--host", "0.0.0.0", "--port", "8000"]