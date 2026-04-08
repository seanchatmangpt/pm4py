# PM4Py Production Image
# Multi-stage build for optimal image size

# Stage 1: Builder
FROM python:3.14-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.14-slim as runtime

# Set runtime arguments
ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PM4PY_HOME=/app \
    PATH=/app/.venv/bin:$PATH

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 pm4py && \
    mkdir -p /app && \
    chown -R pm4py:pm4py /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY --chown=pm4py:pm4py . .

# Install PM4Py in development mode
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER pm4py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pm4py; print('OK')" || exit 1

# Expose port for API (if using FastAPI/Flask wrapper)
EXPOSE 8000

# Default command
CMD ["python", "-m", "pm4py.cli"]
