from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, LoginRequest, LoginResponse
from app.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Реєстрація нового користувача")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Створює нового користувача з хешованим паролем."""
    # Перевірка унікальності username
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Користувач '{user_data.username}' вже існує"
        )

    # Перевірка унікальності email
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_data.email}' вже зареєстровано"
        )

    # Створення користувача з хешованим паролем
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login",
             response_model=LoginResponse,
             summary="Вхід користувача")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Аутентифікація користувача за логіном та паролем."""
    # Пошук користувача
    user = db.query(User).options(joinedload(User.roles)).filter(User.username == credentials.username).first()
    # Захист від enumeration attack — однакове повідомлення про помилку
    if not user or not verify_password(
        credentials.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль"
        )

    # Перевірка активності акаунту
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Акаунт деактивовано"
        )

    # Отримання ролей користувача
    user_roles = [role.name for role in user.roles]

    return LoginResponse(
        message="Вхід успішний",
        user_id=user.id,
        username=user.username,
        roles=user_roles
    )
