from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from datetime import datetime
from .database import Base
from .enums import Grade

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    grade = Column(Enum(Grade), nullable=False)
    institute = Column(String, nullable=False)
    city = Column(String, nullable=False)
    marketing = Column(String, nullable=False)
    
class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
