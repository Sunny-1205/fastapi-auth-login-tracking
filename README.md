# FastAPI Auth Login Tracking

A user authentication REST API built with **FastAPI**, **SQLAlchemy** and **PostgreSQL**. It lets users register and log in, stores passwords using salted PBKDF2 hashing, and records every login attempt (success or failure) in the database. The API and database are deployed on **Railway**.

## Live Demo

- API: https://fastapi-auth-login-tracking-production.up.railway.app
- Swagger docs: https://fastapi-auth-login-tracking-production.up.railway.app/docs

Deployed on Railway with a managed PostgreSQL database and environment-based configuration.

## Features

- User registration with request validation (Pydantic)
- Duplicate username detection (`409 Conflict`)
- Login with credential verification
- Passwords hashed with **PBKDF2-HMAC-SHA256** (600,000 iterations, unique random salt per user)
- Constant-time password comparison
- Login auditing: every attempt is saved with a status (`success` / `failed`) and a detail message
- Endpoint to view login history
- Tables created automatically on startup
- Interactive API docs (Swagger UI and ReDoc)
- Continuous deployment from GitHub to Railway

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Framework | FastAPI |
| Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | PostgreSQL (psycopg v3) |
| Validation | Pydantic |
| Hashing | `hashlib.pbkdf2_hmac` (standard library) |
| Hosting | Railway (API and database) |

## Project Structure

```
auth/
├── db_connection/
│   └── db.py            # Engine, session factory and Base
├── models/
│   └── models.py        # SQLAlchemy models: User, LoginLog, LoginLogDetail
├── schemas/
│   └── schemas.py       # Pydantic schemas: UserCreate, UserLogin
├── main/
│   └── main.py          # FastAPI app, auth logic and routes
├── requirements.txt
├── .env.example
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Sunny-1205/fastapi-auth-login-tracking.git
cd fastapi-auth-login-tracking
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and set your database URL:

```
DATABASE_URL=postgresql+psycopg://user:password@host:port/dbname
```

> **Railway users:** when running locally, use the **public** database URL (`DATABASE_PUBLIC_URL`, host ending in `.proxy.rlwy.net`). The internal `postgres.railway.internal` host only resolves inside Railway's network.

### 4. Run the server

```bash
python -m uvicorn main.main:app --host 127.0.0.1 --port 8000 --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Create a new user |
| POST | `/login` | Authenticate a user and log the attempt |
| GET | `/login-logs` | List login attempts with their details |

### Register

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "sunny", "password": "StrongPass123"}'
```

Responses:

| Status | Meaning |
|--------|---------|
| `200` | `{"message": "User created"}` |
| `409` | `{"detail": "Username already exists"}` |
| `422` | Validation error (missing or invalid fields) |

### Login

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "sunny", "password": "StrongPass123"}'
```

Responses:

| Status | Meaning |
|--------|---------|
| `200` | `{"message": "Login successful"}` |
| `401` | `{"detail": "Invalid username or password"}` |

Both outcomes are written to the login log.

### Login logs

```bash
curl http://127.0.0.1:8000/login-logs
```

Returns every login attempt, newest first, with its details:

```json
{
  "logs": [
    {
      "id": 1,
      "username": "sunny",
      "status": "success",
      "created_at": "2026-10-08T08:15:30.123456",
      "details": [
        {
          "id": 1,
          "detail_key": "message",
          "detail_value": "Login successful",
          "created_at": "2026-10-08T08:15:30.123456"
        }
      ]
    }
  ]
}
```

## Database Design

- **User**: username and the hashed password (stored as `pbkdf2_sha256$iterations$salt$hash`)
- **LoginLog**: one row per login attempt, with the username, status and timestamp
- **LoginLogDetail**: key/value details attached to each log (for example the result message)

## Deployment (Railway)

- The API and PostgreSQL run as two services in one Railway project
- The API connects to the database over Railway's private network using environment variables
- Start command: `uvicorn main.main:app --host 0.0.0.0 --port $PORT`
- Every push to `main` triggers an automatic redeploy

## Security Notes

- Passwords are never stored in plain text
- Credentials are sent in POST request bodies, never in URLs
- Secrets come from environment variables, and `.env` is excluded by `.gitignore`
- Password verification uses `secrets.compare_digest` (constant time)
- Failed logins return the same generic message for unknown users and wrong passwords

## Future Improvements

- JWT access tokens and protected routes
- Authentication for the `/login-logs` endpoint (admin-only access) and pagination
- Minimum password length and strength rules
- Rate limiting and lockout after repeated failed logins
- Automated tests with pytest
- Database migrations with Alembic

## Author

**Sunny** - [GitHub](https://github.com/Sunny-1205)
