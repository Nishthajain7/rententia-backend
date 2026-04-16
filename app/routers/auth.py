import os
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Response, status
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session
from app.crud.user import authenticate_user, create_google_user, get_user, username_exists
from app.dependencies import get_db
from app.schemas.user import (GoogleAuthRequest, GoogleCompleteProfile,
                              GoogleVerifiedResponse, LoginRequest, UserOut)
from app.crud.session import SESSION_TTL_DAYS, create_session

load_dotenv()
ENV = os.getenv("ENV", "development")
COOKIE_SECURE = ENV == "production"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise RuntimeError("GOOGLE_CLIENT_ID environment variable is not set.")

router = APIRouter(prefix="/auth", tags=["Users"])

def _set_session_cookie(response: Response, db: Session, user_id: int):
    session_id = create_session(db, user_id)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=60 * 60 * 24 * SESSION_TTL_DAYS,
    )

def verify_google_token(token: str):
    try:
        return id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID
        )

    except (GoogleAuthError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

# Existing user
@router.post("/username-login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    _set_session_cookie(response, db, user.id)
    return user

@router.post("/google-login", response_model=UserOut)
def google_login(payload: GoogleAuthRequest, response: Response, db: Session = Depends(get_db)):
    idinfo = verify_google_token(payload.token)
    google_id = idinfo["sub"]

    user = get_user(db, google_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please sign up first.",
        )

    _set_session_cookie(response, db, user.id)
    return user

# Google auth of a new user
@router.post("/google-verify", response_model=GoogleVerifiedResponse)
def google_verify(payload: GoogleAuthRequest, db: Session = Depends(get_db)):

    idinfo = verify_google_token(payload.token)
    google_id = idinfo["sub"]

    if get_user(db, google_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists. Please log in.",
        )

    return GoogleVerifiedResponse(
        token=payload.token,
        email=idinfo["email"],
        name=idinfo.get("given_name") or idinfo.get("name", ""),
    )
        
@router.post("/google_register", response_model=UserOut)
def complete_profile(
    payload: GoogleCompleteProfile,
    response: Response,
    db: Session = Depends(get_db),
):
    idinfo = verify_google_token(payload.token)

    google_id = idinfo["sub"]
    email = idinfo["email"]
    name = idinfo.get("given_name") or idinfo.get("name", "")

    if get_user(db, google_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists. Please log in.",
        )

    if username_exists(db, payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    try:
        user = create_google_user(
            db=db,
            google_id=google_id,
            email=email,
            name=name,
            username=payload.username,
            password=payload.password,
            grade=payload.grade,
            institute=payload.institute,
            city=payload.city,
            marketing=payload.marketing,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists",
        )

    _set_session_cookie(response, db, user.id)
    return user
        