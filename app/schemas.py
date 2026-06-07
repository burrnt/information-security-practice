import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

# ── Схеми для реєстрації ──

class UserCreate(BaseModel):
    """Схема запиту на реєстрацію нового користувача."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Логін (латиниця, цифри, підкреслення)"
    )
    email: EmailStr = Field(
        ...,
        description="Email-адреса"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль (мінімум 8 символів)"
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Повне ім'я користувача"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Перевірка складності пароля."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль має містити хоча б одну велику літеру")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль має містити хоча б одну малу літеру")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль має містити хоча б одну цифру")
        return v


class UserResponse(BaseModel):
    """Схема відповіді з даними користувача (без пароля!)."""
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Схеми для входу ──

class LoginRequest(BaseModel):
    """Схема запиту на вхід."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Схема відповіді при успішному вході."""
    message: str
    user_id: int
    username: str
    roles: list[str] = []

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str

    class Config:
        from_attributes = True
