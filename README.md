# FastAPI Auth Login Tracking

A user authentication REST API built with **FastAPI**, **SQLAlchemy** and **PostgreSQL**. It handles user registration and login, stores hashed passwords, and records login activity in the database for auditing.

## Features

- User registration with request validation (Pydantic)
- Login endpoint with credential verification
- Passwords are hashed before storage (no plain-text passwords)
- Login activity logging with separate `LoginLog` and `LoginLogDetail` tables
- Duplicate user detection with clear error responses
- PostgreSQL database hosted on Railway
- Interactive API docs generated automatically (Swagger UI)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Framework | FastAPI |
| Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | PostgreSQL (psycopg v3) |
| Validation | Pydantic |
| Database hosting | Railway |

## Project Structure

```
auth/
├── db_connection/
│   └── db.py          # Engine, session factory and Base
├── models/
│   └── models.py      # SQLAlchemy models: User, LoginLog, LoginLogDetail
├── schemas/
│   └── schemas.py     # Pydantic schemas: UserCreate, UserLogin
├── main/
│   └── main.py        # FastAPI app and routes
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

Create a `.env` file in the project root (see `.env.example`):

```
DATABASE_URL=postgresql+psycopg://user:password@host:port/dbname
```

If you use Railway, run the app locally with the **public** database URL (`DATABASE_PUBLIC_URL`). The internal `postgres.railway.internal` host only works inside Railway's network.

### 4. Run the server

```bash
python -m uvicorn main.main:app --host 127.0.0.1 --port 8000 --reload
```

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

Database tables are created automatically on startup.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register a new user |
| POST | `/login` | Authenticate a user and log the attempt |

### Signup

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "StrongPass123"}'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "StrongPass123"}'
```

Use the **Swagger UI** at `/docs` to see the exact request and response schemas.

## Database Design

- **User**: stores account details and the hashed password
- **LoginLog**: one record per login attempt
- **LoginLogDetail**: extra details for each login attempt

## Security Notes

- Passwords are never stored in plain text
- Credentials are sent via POST request bodies, not URLs
- Secrets are loaded from environment variables
- `.env` is excluded from version control via `.gitignore`
- Use HTTPS in production

## Future Improvements

- JWT access tokens and protected routes
- Rate limiting and account lockout on repeated failed logins
- Automated tests with pytest
- Docker setup and cloud deployment
- Upgrade password hashing to bcrypt or Argon2 (if not already used)

## Author

**Sunny** - [GitHub](https://github.com/Sunny-1205)
