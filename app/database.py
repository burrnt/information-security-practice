from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
		
DATABASE_URL = "sqlite:///./data/app.db"
 
engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False},
)
 
SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
)
 
 
class Base(DeclarativeBase):
	pass
