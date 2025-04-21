FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG UID=1000 \
    GID=1000

# Create base directories with proper structure
RUN mkdir -p /opt/app /opt/db /opt/static

# Create user to run the apps
RUN groupadd -g "${GID}" -r web && \
    useradd -d '/opt/app' -g web -l -r -u "${UID}" web && \
    chown -R web:web /opt

# Copy and setup entrypoint script
COPY docker-entrypoint.sh /opt/
RUN chmod +x /opt/docker-entrypoint.sh && \
    chown web:web /opt/docker-entrypoint.sh

# Switch to non-root user
USER web
WORKDIR /opt/app
