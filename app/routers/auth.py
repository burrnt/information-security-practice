from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from starlette.requests import Request
from app.middleware.rate_limiter import limiter
from jose import JWTError

from app.database import get_db
from app.models import User
# Додано нові Pydantic-схеми для підтримки специфікації JWT-автентифікації
from app.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, TokenRefreshRequest, UserInfo
from app.security import hash_password, verify_password

# Імпорт компонентів криптографічного ядра та інструментів контролю доступу (RBAC)
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user

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


# Аутентифікація користувача за логіном та паролем.
@router.post("/login",
             response_model=TokenResponse,
             summary="Вхід користувача")
@limiter.limit("5/minute")  # Обмеження брутфорсу
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):

    # Пошук користувача з використанням жадібного завантаження (joinedload) для уникнення LazyLoadingError
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

    # Авторизація на основі RBAC: визначення ролі користувача з бази даних
    # (Для генерації access-токену виділяється перша призначена роль, або "student" за замовчуванням)
    role = user.roles[0].name if user.roles else "student"

    # Криптографічне підписання пари токенів за стандартом RFC 7519
    # Access Token — для автентифікації запитів (короткотривалий)
    # Refresh Token — для безпечного оновлення сесії (довготривалий)
    access_token = create_access_token(user.id, role)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


"""
    Реалізація механізму ротації токенів доступу (Token Refresh Flow).
    Дозволяє клієнту отримати новий Access Token без повторного введення пароля.
    """
@router.post("/refresh", 
             response_model=TokenResponse, 
             summary="Оновлення сесії через Refresh Token")
def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    
    try:
        # Криптографічна верифікація підпису та терміну дії Refresh токена
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Невалідний або протермінований refresh token"
        )

    # Контроль цілісності призначення: токен має належати до типу 'refresh'
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Наданий токен не є токеном оновлення сесії"
        )

    # Отримання ідентифікатора користувача (Subject claim) з Payload JWT
    user_id = int(payload["sub"])
    user = db.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача, пов'язаного з токеном, не знайдено")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Акаунт деактивовано")

    # Перевипуск нової пари токенів (Access + Refresh) для запобігання replay-атакам
    role = user.roles[0].name if user.roles else "student"
    return TokenResponse(
        access_token=create_access_token(user.id, role),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer"
    )


# Ендпоїнт для перевірки статусу поточної сесії
@router.get("/me", 
            response_model=UserInfo, 
            summary="Профіль автентифікованого користувача")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Захищений маршрут, що демонструє роботу FastAPI Dependency Injection.
    Повертає інформацію про користувача, чий токен пройшов перевірку в get_current_user.
    """
    # Формування поточної ролі об'єкта для повернення згідно Pydantic-схеми UserInfo
    role = current_user.roles[0].name if current_user.roles else "student"
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=role,
    )
