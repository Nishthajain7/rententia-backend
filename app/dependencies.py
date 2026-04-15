from datetime import datetime, timezone
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.crud.user import get_user_by_id
from app.database import SessionLocal
from app.models import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    session_id: str = Cookie(None),
    db: DBSession = Depends(get_db)
):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db_session = (
        db.query(Session)
        .filter(Session.id == session_id)
        .first()
    )

    if not db_session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    if db_session.expires_at.tzinfo is None:
        expires_at = db_session.expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = db_session.expires_at

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    user = get_user_by_id(db, db_session.user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user