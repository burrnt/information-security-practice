from app.audit.middleware import AuditMiddleware
from app.audit.router import router as audit_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.routers import auth, students, teachers, admin
from app.database import engine, Base
from app.seed import seed
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiter import limiter
import app.models


# Цей рядок автоматично створить .db файл та всі таблиці, якщо їх немає
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Електронний деканат",
    description="API для управління академічними даними",
    version="0.8.0"
)
app.add_middleware(AuditMiddleware)

# Реєстрація обробника для гарної віддачі помилки 429 (Too Many Requests)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Підключення Middleware
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3010"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Підключення роутерів
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(admin.router)
app.include_router(audit_router, prefix="/api/v1/admin", tags=["audit"])

@app.get("/")
def root():
	return {"message": "Електронний деканат API v0.6.0. Захист від XSS/CSRF активовано."}
 
 
@app.get("/health")
def health_check():
	return {
    	"status": "healthy",
    	"database": "SQLite",
    	"tables": len(Base.metadata.tables)
	}

@app.on_event("startup")
def on_startup():
    print("Запуск додатку: перевірка початкових даних...")
    seed()
