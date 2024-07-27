# app/vector_search.py
import spacy
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import KnowledgeFragment

nlp = spacy.load("en_core_web_md")

def vectorize_text(text: str) -> bytes:
    doc = nlp(text)
    vector = doc.vector
    return vector.tobytes()

async def search_vectors(query_vector: bytes, db: AsyncSession):
    query_vector = np.frombuffer(query_vector, dtype=np.float32)
    results = await db.execute(select(KnowledgeFragment))
    fragments = results.scalars().all()
    fragments.sort(key=lambda x: np.linalg.norm(np.frombuffer(x.vector, dtype=np.float32) - query_vector))
    return fragments[:5]  # Return top 5 most similar fragments

