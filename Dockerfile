FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000


CMD ["sh", "scripts/web.sh"]
    