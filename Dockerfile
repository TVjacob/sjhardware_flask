# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client for psql debugging
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Set environment variables (optional)
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Expose the port your Flask app runs on
EXPOSE 5000

# Command to run the app with a longer timeout (e.g., 120s)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "run:app"]
