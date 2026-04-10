from pydantic import BaseModel, EmailStr, field_validator
import uuid
from ..models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class SetParentPinRequest(BaseModel):
    pin: str
    current_pin: str | None = None  # Required to change existing PIN

    @field_validator("pin")
    @classmethod
    def pin_format(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 4:
            raise ValueError("Le PIN doit contenir exactement 4 chiffres")
        return v


class VerifyParentPinRequest(BaseModel):
    pin: str
    task_id: str | None = None  # Optional: bind token to a specific task


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    avatar_url: str | None
    locale: str
    is_active: bool
    is_child_profile: bool
    has_parent_pin: bool

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class ParentTokenResponse(BaseModel):
    parent_token: str
