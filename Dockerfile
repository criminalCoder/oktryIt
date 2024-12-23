# Base image with Python 3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    python3-pip \
    && apt-get clean

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Command to run the bot
CMD ["python3", "bot.py"]
