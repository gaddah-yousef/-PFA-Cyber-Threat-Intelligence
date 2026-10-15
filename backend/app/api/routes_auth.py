from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, require_roles
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, UserRead, UserUpdate
from app.services.audit_log_service import record_audit_log

router = APIRouter(prefix="/api/auth", tags=["Auth"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> Token:
    user = db.scalar(select(User).where(User.email == form_data.username))
    if not user or not user.is_active or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = create_access_token(subject=user.id, role=user.role)
    record_audit_log(db, user, action="auth.login", target_type="user", target_id=user.id)
    return Token(access_token=token, role=UserRole(user.role), email=user.email)


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser) -> User:
    return current_user


@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def create_user(payload: UserCreate, db: DbSession, current_user: CurrentUser) -> User:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà",
        )
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_audit_log(
        db,
        current_user,
        action="auth.create_user",
        target_type="user",
        target_id=user.id,
        details=f"role={user.role}",
    )
    return user


@router.get(
    "/users",
    response_model=list[UserRead],
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def list_users(db: DbSession) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


@router.patch(
    "/users/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def update_user(
    user_id: str, payload: UserUpdate, db: DbSession, current_user: CurrentUser
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    changes = payload.model_dump(exclude_unset=True)
    if user.id == current_user.id and changes.get("is_active") is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas désactiver votre propre compte",
        )
    if (
        user.id == current_user.id
        and changes.get("role") is not None
        and changes["role"] != UserRole.admin
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas retirer votre propre rôle administrateur",
        )
    if "role" in changes and changes["role"] is not None:
        user.role = changes["role"].value
    if "is_active" in changes and changes["is_active"] is not None:
        user.is_active = changes["is_active"]
    db.commit()
    db.refresh(user)
    record_audit_log(
        db,
        current_user,
        action="auth.update_user",
        target_type="user",
        target_id=user.id,
        details=f"role={user.role} is_active={user.is_active}",
    )
    return user
