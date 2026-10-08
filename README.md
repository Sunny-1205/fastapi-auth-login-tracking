FastAPI Auth Login Tracking

A user authentication REST API built with FastAPI, SQLAlchemy and PostgreSQL. It lets users register and log in, stores passwords using salted PBKDF2 hashing, and records every login attempt (success or failure) in the database. An admin-protected endpoint exposes the login history.

Features
User registration with input validation (Pydantic)
Duplicate username detection (409 Conflict)
Login with credential verification
Passwords hashed with PBKDF2-HMAC-SHA256 (600,000 iterations, unique random salt per user)
Constant-time password comparison
Timing-attack mitigation: unknown usernames take as long to reject as real ones, so valid usernames can't be guessed from response time
Login auditing: every attempt is saved with a status (success / failed) and a detail message
Admin-only login history endpoint (X-Admin-Key header) with pagination
Tables created automatically on startup
Interactive API docs (Swagger UI and ReDoc)
Tech Stack
Layer	Technology
Language	Python 3.11
Framework	FastAPI
Server	Uvicorn
ORM	SQLAlchemy
Database	PostgreSQL (psycopg v3), hosted on Railway
Validation	Pydantic
Hashing	hashlib.pbkdf2_hmac (standard library)
Project Structure
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
Getting Started
1. Clone the repository
bash
git clone https://github.com/Sunny-1205/fastapi-auth-login-tracking.git
cd fastapi-auth-login-tracking
2. Create a virtual environment and install dependencies
bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
3. Configure environment variables

Copy .env.example to .env and fill in your values:

Variable	Description
DATABASE_URL	PostgreSQL connection string using the psycopg driver
ADMIN_API_KEY	Secret key required to read /login-logs
DATABASE_URL=postgresql+psycopg://user:password@host:port/dbname
ADMIN_API_KEY=change-me

Generate a strong admin key with:

bash
python -c "import secrets; print(secrets.token_urlsafe(32))"

Railway users: when running locally, use the public database URL (DATABASE_PUBLIC_URL, host ending in .proxy.rlwy.net). The internal postgres.railway.internal host only resolves inside Railway's network.

4. Run the server
bash
python -m uvicorn main.main:app --host 127.0.0.1 --port 8000 --reload
API: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
API Endpoints
Method	Endpoint	Auth	Description
POST	/register	None	Create a new user
POST	/login	None	Authenticate a user and log the attempt
GET	/login-logs	X-Admin-Key header	List login attempts with details (paginated)
Register
bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "sunny", "password": "StrongPass123"}'

Responses:

Status	Meaning
201	{"message": "User created"}
409	{"detail": "Username already exists"}
422	Validation error (for example, password too short)
Login
bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "sunny", "password": "StrongPass123"}'

Responses:

Status	Meaning
200	{"message": "Login successful"}
401	{"detail": "Invalid username or password"}

Both outcomes are written to the login log.

Login logs (admin only)
bash
curl "http://127.0.0.1:8000/login-logs?limit=20&offset=0" \
  -H "X-Admin-Key: your-admin-key"

Query parameters:

Parameter	Default	Range	Description
limit	50	1 to 200	Number of logs to return
offset	0	0 or more	Number of logs to skip

Example response:

json
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
Status	Meaning
200	Logs returned, newest first
403	Wrong or unconfigured admin key
422	X-Admin-Key header missing
Database Design
User: username and the hashed password (stored as pbkdf2_sha256$iterations$salt$hash)
LoginLog: one row per login attempt, with the username, status and timestamp
LoginLogDetail: key/value details attached to each log (for example the result message)
Security Notes
Passwords are never stored in plain text
Credentials are sent in POST request bodies, never in URLs
Secrets come from environment variables, and .env is excluded by .gitignore
Password verification uses secrets.compare_digest (constant time)
Failed logins return the same generic message for unknown users and wrong passwords
Login history is not public and requires an admin key
Run behind HTTPS in production
Future Improvements
JWT access tokens and protected user routes
Rate limiting and temporary lockout after repeated failed logins
Automated tests with pytest
Docker setup and cloud deployment
Database migrations with Alembic
## Author

**Sunny** - [GitHub](https://github.com/Sunny-1205)
