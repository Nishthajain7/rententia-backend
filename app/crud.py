from sqlalchemy.orm import Session
from app import models
from app.enums import Grade

def get_user(db: Session, google_id: str):
    return db.query(models.User).filter(models.User.google_id == google_id).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_google_user(
    db: Session,
    google_id: str,
    email: str,
    name: str,
    grade: Grade,
    institute: str,
    city: str,
    marketing: str):
    user = models.User(
        google_id=google_id,
        email=email,
        name=name,
        grade=grade,
        institute=institute,
        city=city,
        marketing=marketing,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

