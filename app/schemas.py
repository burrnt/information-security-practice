import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from app.validators import sanitizer

# Схеми для реєстрації

class UserCreate(BaseModel):
    """Схема реєстрації з суворою серверною валідацією та санітизацією вводу."""
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        v = sanitizer.sanitize_text(v)
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Логін: лише латинські літери, цифри та _")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        # 1. Захист від XSS
        cleaned = sanitizer.sanitize_text(v)
        if v != cleaned or re.search(r"[<>&\"']", v):
            raise ValueError("HTML-теги або символи ін'єкцій < > & \" в імені суворо заборонені")
        
        # 2. Захист від SQL Injection
        if sanitizer.contains_sql_patterns(v):
            raise ValueError("Виявлено підозрілі SQL-патерни в імені")
        return cleaned.strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Потрібна хоча б одна велика літера")
        if not re.search(r"[a-z]", v):
            raise ValueError("Потрібна хоча б одна мала літера")
        if not re.search(r"\d", v):
            raise ValueError("Потрібна хоча б одна цифра")
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
