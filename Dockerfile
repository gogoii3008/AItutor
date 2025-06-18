# Use Python 3.11 base image
FROM python:3.11-slim

# Install system packages (including ffmpeg)
RUN apt-get update && apt-get install -y ffmpeg

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Start your app
CMD ["python", "app.py"]
