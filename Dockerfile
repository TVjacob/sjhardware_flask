# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables (optional)
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Expose the port your Flask app runs on
EXPOSE 5000

# Command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
