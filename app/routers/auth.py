from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app import crud
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv
import os
from app.schemas import user
from app.utils.session import create_session


load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
router = APIRouter(prefix="/auth", tags=["Users"])

@router.post("/google-auth", response_model=user.UserOut)
def google_login(
    payload: user.GoogleAuthRequest,
    response: Response,
    db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(payload.token, requests.Request(), GOOGLE_CLIENT_ID)
        google_id = idinfo["sub"]
        db_user = crud.get_user(db, google_id)
        
        if db_user:
            session_id = create_session(db, db_user.id)
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=60 * 60 * 24 * 7,
            )
            return db_user
        
        raise HTTPException(status_code=409,detail="COMPLETE_PROFILE_REQUIRED")

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
        
@router.post("/complete-profile", response_model=user.UserOut)
def complete_profile(
    payload: user.GoogleCompleteProfile,
    response: Response,
    db: Session = Depends(get_db)
):
    try:
        idinfo = id_token.verify_oauth2_token(payload.token,requests.Request(),GOOGLE_CLIENT_ID)

        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("given_name") or idinfo.get("name")

        db_user = crud.get_user(db, google_id)
        
        if db_user:
            return db_user

        user = crud.create_google_user(
            db=db,
            google_id=google_id,
            email=email,
            name=name,
            grade=payload.grade,
            institute=payload.institute,
            city=payload.city,
            marketing=payload.marketing,
        )
        session_id = create_session(db, user.id)
        response.delete_cookie("oauth_pending")
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
        )

        return user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )