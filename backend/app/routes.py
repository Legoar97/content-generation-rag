# app/routes.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from .database import get_db
from .models import Document, KnowledgeFragment
from .schemas import DocumentCreate, QueryRequest, DocumentResponse, DataStats
from .vector_search import vectorize_text, search_vectors
from .data_ingestion import ingest_wikipedia_data, ingest_rss_feed
import openai
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Carga las variables de entorno desde el archivo .env

router = APIRouter()

openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/add_document/", response_model=DocumentResponse)
async def add_document(document: DocumentCreate, db: AsyncSession = Depends(get_db)):
    vector = vectorize_text(document.content)
    db_document = Document(title=document.title, content=document.content, vector=vector)
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    
    fragments = document.content.split('. ')  # Simple split by sentences for example
    for fragment in fragments:
        fragment_vector = vectorize_text(fragment)
        db_fragment = KnowledgeFragment(document_id=db_document.id, fragment=fragment, vector=fragment_vector)
        db.add(db_fragment)
    await db.commit()
    
    return db_document

@router.post("/generate_content/")
async def generate_content(query: QueryRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Vectorizar la consulta
        query_vector = vectorize_text(query.text)
        
        # Buscar fragmentos relevantes
        fragments = await search_vectors(query_vector, db)
        
        if not fragments:
            return {"response": "No se encontraron datos relevantes para generar una respuesta."}
        
        # Preparar el contexto para OpenAI
        context = " ".join([fragment.fragment for fragment in fragments])
        
        # Generar respuesta con OpenAI
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"{context}\n\nQ: {query.text}\nA:",
                max_tokens=150
            )
            return {"response": response.choices[0].text.strip()}
        except openai.error.OpenAIError as e:
            print(f"Error de OpenAI: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al comunicarse con OpenAI: {str(e)}")
        
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/ingest_wikipedia/")
async def trigger_wikipedia_ingestion(background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_wikipedia_data, "artificial intelligence")
    return {"message": "Wikipedia ingestion started in the background"}

@router.post("/ingest_rss/")
async def trigger_rss_ingestion(background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_rss_feed, "http://rss.cnn.com/rss/edition.rss")
    return {"message": "RSS feed ingestion started in the background"}

@router.get("/data_stats/", response_model=DataStats)
async def get_data_stats(db: AsyncSession = Depends(get_db)):
    try:
        doc_count = await db.execute(select(func.count(Document.id)))
        frag_count = await db.execute(select(func.count(KnowledgeFragment.id)))
        
        return DataStats(
            document_count=doc_count.scalar(),
            fragment_count=frag_count.scalar()
        )
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas de la base de datos")

@router.post("/test_vector_search/")
async def test_vector_search(query: QueryRequest, db: AsyncSession = Depends(get_db)):
    try:
        query_vector = vectorize_text(query.text)
        fragments = await search_vectors(query_vector, db)
        return {"fragments": [f.fragment for f in fragments]}
    except Exception as e:
        print(f"Error en la búsqueda vectorial: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la búsqueda vectorial: {str(e)}")