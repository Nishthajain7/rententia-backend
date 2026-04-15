from sqlalchemy.orm import Session
from app.enums import Grade
from app.models import User
from app.utils.hashing import hash_password, verify_password

def get_user(db: Session, google_id: str):
    return db.query(User).filter(User.google_id == google_id).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_google_user(
    db: Session,
    google_id: str,
    email: str,
    name: str,
    username: str,
    password: str,
    grade: Grade,
    institute: str,
    city: str,
    marketing: str):
    user = User(
        google_id=google_id,
        email=email,
        name=name,
        username=username,
        password=hash_password(password),
        grade=grade,
        institute=institute,
        city=city,
        marketing=marketing,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
