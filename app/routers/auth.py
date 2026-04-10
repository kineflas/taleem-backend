from datetime import datetime, timedelta, timezone
import random
import string
import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from ..core.dependencies import CurrentUser, DB
from ..core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    create_parent_token, decode_token, verify_parent_token,
)
from ..models.user import User, UserRole
from ..models.streak import Streak
from ..schemas.auth import (
    RegisterRequest, LoginRequest, RefreshRequest,
    SetParentPinRequest, VerifyParentPinRequest,
    AuthResponse, UserOut, ParentTokenResponse,
)
from ..services.streak_service import init_streak_for_student

router = APIRouter(prefix="/auth", tags=["Auth"])


def _build_auth_response(user: User, db: Session) -> AuthResponse:
    access = create_access_token(str(user.id), user.role.value)
    refresh = create_refresh_token(str(user.id))
    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserOut.model_validate(user),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: DB):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    db.add(user)
    db.flush()

    # Init streak for students
    if body.role == UserRole.STUDENT:
        init_streak_for_student(db, user.id)

    db.commit()
    db.refresh(user)
    return _build_auth_response(user, db)


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: DB):
    user = db.query(User).filter(User.email == body.email, User.is_active == True).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    return _build_auth_response(user, db)


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(body: RefreshRequest, db: DB):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Token invalide")
        user_id = payload.get("sub")
    except ValueError:
        raise HTTPException(status_code=401, detail="Refresh token invalide ou expiré")

    user = db.query(User).filter(User.id == uuid.UUID(user_id), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    return _build_auth_response(user, db)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: CurrentUser):
    # Stateless JWT — client deletes tokens. Could blacklist here if needed.
    pass


@router.get("/me", response_model=UserOut)
def me(current_user: CurrentUser):
    return UserOut.model_validate(current_user)


@router.post("/set-parent-pin", status_code=status.HTTP_204_NO_CONTENT)
def set_parent_pin(body: SetParentPinRequest, current_user: CurrentUser, db: DB):
    # If PIN already set, require current PIN
    if current_user.parent_pin_hash:
        if not body.current_pin:
            raise HTTPException(status_code=400, detail="L'ancien PIN est requis pour le modifier")
        if not verify_password(body.current_pin, current_user.parent_pin_hash):
            raise HTTPException(status_code=400, detail="Ancien PIN incorrect")

    current_user.parent_pin_hash = hash_password(body.pin)
    current_user.is_child_profile = True
    db.commit()


@router.post("/verify-parent-pin", response_model=ParentTokenResponse)
def verify_parent_pin_endpoint(body: VerifyParentPinRequest, current_user: CurrentUser, db: DB):
    if not current_user.parent_pin_hash:
        raise HTTPException(status_code=400, detail="Aucun PIN parental configuré")

    if not verify_password(body.pin, current_user.parent_pin_hash):
        raise HTTPException(status_code=401, detail="PIN incorrect")

    task_id = body.task_id or "generic"
    token = create_parent_token(str(current_user.id), task_id)
    return ParentTokenResponse(parent_token=token)
