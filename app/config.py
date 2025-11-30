import os

class Config:
    # Connect to the PostgreSQL container on the same Docker network
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:password1@db:5432/sjhardware'  # db is the service name in docker-compose
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
