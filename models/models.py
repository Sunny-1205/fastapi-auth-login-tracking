from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from db_connection.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    details = relationship("LoginLogDetail", back_populates="login_log", cascade="all, delete-orphan")


class LoginLogDetail(Base):
    __tablename__ = "login_log_details"

    id = Column(Integer, primary_key=True, index=True)
    login_log_id = Column(Integer, ForeignKey("login_logs.id"), nullable=False)
    detail_key = Column(String(50), nullable=False)
    detail_value = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    login_log = relationship("LoginLog", back_populates="details")