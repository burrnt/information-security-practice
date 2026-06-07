from fastapi import FastAPI
from app.routers import auth
from app.database import engine, Base
import app.models

# Цей рядок автоматично створить .db файл та всі таблиці, якщо їх немає
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Електронний деканат",
    description="API для управління академічними даними",
    version="0.4.0"
)

# Підключення роутерів
app.include_router(auth.router)
 
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
