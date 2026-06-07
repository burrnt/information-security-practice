from fastapi import FastAPI
from app.routers import auth
from app.database import engine, Base
from app.seed import seed
import app.models

from app.routers import auth
from app.routers import students
from app.routers import teachers
from app.routers import admin

# Цей рядок автоматично створить .db файл та всі таблиці, якщо їх немає
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Електронний деканат",
    description="API для управління академічними даними",
    version="0.5.0"
)

# Підключення роутерів
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(admin.router)

@app.get("/")
def root():
	return {"message":"Електронний деканат API v0.4.0"}
 
 
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
