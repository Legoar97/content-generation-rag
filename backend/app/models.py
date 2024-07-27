# app/models.py
from sqlalchemy import Column, Integer, String, Text, BLOB, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    vector = Column(BLOB)

class KnowledgeFragment(Base):
    __tablename__ = "knowledge_fragments"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    fragment = Column(Text)
    vector = Column(BLOB)
