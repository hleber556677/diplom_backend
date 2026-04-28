from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.dependencies import get_admin_user
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return create_user_record(user_data, db)


@router.post("/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    return create_user_record(user_data, db)


def create_user_record(user_data: UserCreate, db: Session) -> User:
    if user_data.email.lower() == settings.admin_email:
        raise HTTPException(status_code=400, detail="This email is reserved for admin access")

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = User(
        email=user_data.email,
        display_name=user_data.display_name,
        hashed_password=hash_password(user_data.password),
        total_points=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(credentials: LoginRequest, db: Session = Depends(get_db)):
    if (
        credentials.email.lower() == settings.admin_email
        and credentials.password == settings.admin_password
    ):
        user = db.query(User).filter(User.email == settings.admin_email).first()
        if user is None:
            user = User(
                email=settings.admin_email,
                display_name=settings.admin_display_name,
                hashed_password=hash_password(settings.admin_password),
                total_points=0,
            )
            db.add(user)
        else:
            user.display_name = settings.admin_display_name
            user.hashed_password = hash_password(settings.admin_password)
        db.commit()
        db.refresh(user)
        access_token = create_access_token(subject=user.email)
        return {"access_token": access_token, "token_type": "bearer"}

    user = db.query(User).filter(User.email == credentials.email).first()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
