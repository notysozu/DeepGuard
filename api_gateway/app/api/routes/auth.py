from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.crud import create_user, get_user_by_username, list_users
from database.session import get_db
from shared.schemas import Token, UserCreate, UserPublic, UsersResponse
from shared.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    require_role,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)


@router.post("/users", response_model=UserPublic)
def create_user_account(
    payload: UserCreate,
    _: object = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    existing = get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = create_user(
        db,
        username=payload.username,
        password=payload.password,
        role=payload.role,
        is_active=payload.is_active,
    )
    return UserPublic(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.get("/users", response_model=UsersResponse)
def list_user_accounts(
    limit: int = 100,
    _: object = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    users = list_users(db, limit=limit)
    return UsersResponse(
        items=[
            UserPublic(
                id=u.id,
                username=u.username,
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at,
            )
            for u in users
        ]
    )
