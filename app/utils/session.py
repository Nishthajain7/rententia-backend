import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from app.models import Session

SESSION_TTL_DAYS = 7

def create_session(db: DBSession, user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=SESSION_TTL_DAYS)

    db_session = Session(
        id=session_id,
        user_id=user_id,
        expires_at=expires_at,
    )

    db.add(db_session)
    db.commit()

    return session_id
