FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY web_all/ ./web_all/
COPY cli.py .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Install Playwright browsers
RUN playwright install chromium

# Create output directory
RUN mkdir -p /app/output

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "cli.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
