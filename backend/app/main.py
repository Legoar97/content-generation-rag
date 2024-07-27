# app/main.py
from fastapi import FastAPI
from .routes import router
from .database import engine, Base
from .data_ingestion import schedule_data_ingestion

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    schedule_data_ingestion()

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Content Generation RAG API"}


