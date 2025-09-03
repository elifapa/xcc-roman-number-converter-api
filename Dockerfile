FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app/xcc-roman-converter-api
WORKDIR /app/xcc-roman-converter-api

# Copy local dependency source code
# COPY ../xcc-roman-converter /xcc-roman-converter/

# Install the dependencies.
RUN uv sync --frozen --no-cache

# Run the application.
# CMD ["uv", "run", "uvicorn", "src.xcc_roman_converter_api.my_api:app", "--port", "8000", "--host", "0.0.0.0"]
CMD ["sh", "-c", "uv run uvicorn src.xcc_roman_converter_api.my_api:app --port ${PORT:-8000} --host 0.0.0.0 --reload"]

# Health check endpoint for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1