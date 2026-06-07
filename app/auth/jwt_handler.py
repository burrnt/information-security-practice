# app/auth/jwt_handler.py
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
 
 
def create_access_token(user_id: int, role: str) -> str:
	"""
	Генерує short-lived access token.
	Payload містить: sub (user ID), role, exp (час закінчення), type.
	"""
	expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	payload = {
    	"sub": str(user_id),
    	"role": role,
    	"exp": expire,
    	"type": "access"
	}
	return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
 
 
def create_refresh_token(user_id: int) -> str:
	"""
	Генерує long-lived refresh token.
	Містить лише sub та exp — мінімум інформації.
	"""
	expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
	payload = {
    	"sub": str(user_id),
    	"exp": expire,
    	"type": "refresh"
	}
	return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
 
 
def verify_token(token: str) -> dict:
	"""
	Декодує та перевіряє JWT.
	Повертає payload або піднімає JWTError.
	python-jose автоматично перевіряє:
  	- підпис (Signature)
  	- термін дії (exp claim)
	"""
	return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
