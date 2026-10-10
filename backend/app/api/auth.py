from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import Credentials, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(credentials: Credentials, db: Session = Depends(get_db)):
    email = credentials.email.strip().lower()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(id=str(uuid4()), email=email, hashed_password=hash_password(credentials.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id), user=user)


@router.post("/login", response_model=TokenResponse)
def login(credentials: Credentials, db: Session = Depends(get_db)):
    email = credentials.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return user