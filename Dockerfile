# Multi-stage Dockerfile for Google Maps Reviews Dashboard
# Optimized for production deployment with security best practices

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies to /install prefix
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder to system location
COPY --from=builder /install /usr/local

# Copy application files (all Python files and necessary resources)
COPY database_dashboard.py .
COPY database_test.py .
COPY background_scheduler.py .
COPY turkish_time_parser.py .
COPY run_scheduler_standalone.py .
COPY run_scheduler.bat .
COPY api_pipeline/ ./api_pipeline/
COPY scheduler_config.json .
COPY .env* ./

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/archived_data && \
    chmod 755 /app/data /app/archived_data

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')" || exit 1

# Expose port
EXPOSE 8501

# Run as non-root user (security best practice)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["streamlit", "run", "database_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
