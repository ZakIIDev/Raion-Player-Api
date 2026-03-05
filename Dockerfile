FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Install Node.js for yt-dlp
RUN apt-get update && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
# Ensure latest yt-dlp to bypass bot detection
RUN pip install -U yt_dlp

COPY . .

# Use the PORT environment variable provided by Render, defaulting to 10000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
