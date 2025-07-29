FROM python:3.11-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache gcc musl-dev linux-headers tzdata && \
    pip install --no-cache-dir watchdog python-dotenv requests && \
    # Create user with specific UID matching host
    adduser -D -u 1000 monitor && \
    # Create log directory
    mkdir -p /var/log && \
    # Create up build directory
    mkdir -p /alerts && \
    # Clean up build dependencies
    apk del gcc musl-dev linux-headers

# Copy application files (as root)
COPY --chown=monitor:monitor monitor.py logs_and_alerts.py requirements.txt ./

# Set proper permissions for log file
RUN touch /var/log/auth.log && \
    chown monitor:monitor /var/log/auth.log && \
    chmod 644 /var/log/auth.log && \
    chown monitor:monitor /alerts && \
    chmod 755 /alerts

USER monitor

CMD ["python", "monitor.py"]
