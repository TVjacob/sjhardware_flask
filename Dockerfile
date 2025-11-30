# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client for debugging / migrations
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

# Expose the port your Flask app runs on
EXPOSE 5000

# Command to run the app directly (no Gunicorn)
CMD ["python", "run.py"]
