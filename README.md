# Document Management API

A REST API for managing documents, built with FastAPI.

Features

CRUD operations for documents

JWT authentication

User-specific document access

Role-based access control for admin endpoints

Request validation with Pydantic

PostgreSQL database

Database migrations with Alembic

Automated tests with pytest

Docker Compose setup

Tech Stack

Python

FastAPI

SQLAlchemy

PostgreSQL

Alembic

Pydantic

Pytest

Docker Compose

Run with Docker

Configure your .env file with the required PostgreSQL variables and SECRET_KEY.

Start the services:

docker compose up --build

Open the API documentation:

http://localhost:8000/docs

Run Tests

Activate your virtual environment and run:

pytest -q

The test suite covers authentication, document operations, request validation, and access control.

Database Migrations

Apply database migrations with:

alembic upgrade head

Run migrations only after configuring the database connection for the intended environment.

Security Notes

Do not commit .env or real credentials.

Use a strong, unique SECRET_KEY.

Keep the test database separate from the development database.