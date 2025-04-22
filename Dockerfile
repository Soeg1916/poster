FROM python:3.11-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY pyproject.toml .
COPY uv.lock .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
# IMPORTANT: Add this line to bypass conflict check
ENV BYPASS_CONFLICT_CHECK=true

# Make scripts executable
RUN chmod +x run_miku_bot_standalone.py

# Command to run the application with healthcheck server
CMD ["python", "healthcheck.py"]
