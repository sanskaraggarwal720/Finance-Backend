from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.deps import require_admin, require_viewer_or_above
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Admin only: create a new user."""
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="A user with this email already exists.")
    user = User(**payload.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=List[UserRead])
def list_users(
    session: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
):
    """All authenticated users can list users."""
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Admin only: update user details or role."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def deactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Admin only: deactivate (soft-delete) a user."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = False
    session.add(user)
    session.commit()
