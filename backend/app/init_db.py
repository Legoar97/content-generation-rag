# app/init_db.py
from .database import engine
from .models import Base

def init_database():
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    init_database()
