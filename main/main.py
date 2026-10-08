import hashlib
import secrets
from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db_connection.db import Base, SessionLocal, engine
from models.models import LoginLog, LoginLogDetail, User
from schemas.schemas import UserCreate, UserLogin

app = FastAPI()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    iterations = 600_000
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return f"pbkdf2_sha256${iterations}${salt.hex()}${password_hash.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, hash_hex = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    salt = bytes.fromhex(salt_hex)
    expected_hash = bytes.fromhex(hash_hex)
    derived_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        int(iterations),
    )

    return secrets.compare_digest(derived_hash.hex(), expected_hash.hex())


def log_login_event(db: Session, username: str, status: str, message: str) -> None:
    log_entry = LoginLog(username=username, status=status)
    db.add(log_entry)
    db.flush()

    detail_entry = LoginLogDetail(
        login_log_id=log_entry.id,
        detail_key="message",
        detail_value=message,
    )
    db.add(detail_entry)
    db.commit()


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)) -> dict[str, str]:
    hashed = hash_password(user.password)
    db_user = User(username=user.username, password=hashed)

    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        ) from error

    return {"message": "User created"}


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)) -> dict[str, str]:
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.password):
        log_login_event(db, user.username, "failed", "Invalid username or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    log_login_event(db, user.username, "success", "Login successful")
    return {"message": "Login successful"}


@app.get("/login-logs")
def get_login_logs(db: Session = Depends(get_db)) -> dict[str, list[dict[str, object]]]:
    logs = db.query(LoginLog).order_by(LoginLog.created_at.desc()).all()
    return {
        "logs": [
            {
                "id": log.id,
                "username": log.username,
                "status": log.status,
                "created_at": log.created_at.isoformat() if log.created_at else "",
                "details": [
                    {
                        "id": detail.id,
                        "detail_key": detail.detail_key,
                        "detail_value": detail.detail_value,
                        "created_at": detail.created_at.isoformat() if detail.created_at else "",
                    }
                    for detail in log.details
                ],
            }
            for log in logs
        ]
    }