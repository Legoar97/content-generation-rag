# backend/app/data_ingestion.py
import requests
import feedparser
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from .database import engine
from .models import Document, KnowledgeFragment
from .vector_search import vectorize_text

async def ingest_wikipedia_data(search_term):
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_term,
        "utf8": 1,
        "srlimit": 10  # Limitar a 10 resultados por búsqueda
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    async with AsyncSession(engine) as db:
        for item in data['query']['search']:
            title = item['title']
            content = item['snippet']
            full_content_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&titles={title}&format=json&explaintext"
            full_content_response = requests.get(full_content_url)
            full_content_data = full_content_response.json()
            page_id = list(full_content_data['query']['pages'].keys())[0]
            full_content = full_content_data['query']['pages'][page_id]['extract']
            
            vector = vectorize_text(full_content)
            
            document = Document(
                title=title,
                content=full_content,
                vector=vector
            )
            db.add(document)
            await db.flush()
            
            # Dividir el contenido en fragmentos y crear KnowledgeFragments
            fragments = split_content(full_content)
            for fragment in fragments:
                fragment_vector = vectorize_text(fragment)
                knowledge_fragment = KnowledgeFragment(
                    document_id=document.id,
                    fragment=fragment,
                    vector=fragment_vector
                )
                db.add(knowledge_fragment)
        
        await db.commit()

async def ingest_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    
    async with AsyncSession(engine) as db:
        for entry in feed.entries:
            title = entry.title
            content = entry.summary
            vector = vectorize_text(content)
            
            document = Document(
                title=title,
                content=content,
                vector=vector
            )
            db.add(document)
            await db.flush()
            
            # Dividir el contenido en fragmentos y crear KnowledgeFragments
            fragments = split_content(content)
            for fragment in fragments:
                fragment_vector = vectorize_text(fragment)
                knowledge_fragment = KnowledgeFragment(
                    document_id=document.id,
                    fragment=fragment,
                    vector=fragment_vector
                )
                db.add(knowledge_fragment)
        
        await db.commit()

def split_content(content, max_length=500):
    # Implementa la lógica para dividir el contenido en fragmentos más pequeños
    # Este es un ejemplo simple, puedes ajustarlo según tus necesidades
    words = content.split()
    fragments = []
    current_fragment = []
    
    for word in words:
        current_fragment.append(word)
        if len(' '.join(current_fragment)) > max_length:
            fragments.append(' '.join(current_fragment[:-1]))
            current_fragment = [word]
    
    if current_fragment:
        fragments.append(' '.join(current_fragment))
    
    return fragments

def schedule_data_ingestion():
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler = AsyncIOScheduler()
    
    # Programa la ingestión de Wikipedia cada 12 horas
    scheduler.add_job(ingest_wikipedia_data, 'interval', hours=12, args=['artificial intelligence'])
    
    # Programa la ingestión de RSS cada hora
    scheduler.add_job(ingest_rss_feed, 'interval', hours=1, args=['http://rss.cnn.com/rss/edition.rss'])
    
    scheduler.start()