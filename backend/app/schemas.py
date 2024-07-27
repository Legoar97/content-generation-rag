# app/schemas.py
from pydantic import BaseModel

class DocumentCreate(BaseModel):
    title: str
    content: str

class QueryRequest(BaseModel):
    text: str

class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True

class DataStats(BaseModel):
    document_count: int
    fragment_count: int