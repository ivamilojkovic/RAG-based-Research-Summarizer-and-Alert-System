from fastapi import FastAPI
from app.db.postgres import PostgresDB, schema
from app.ingestors.pubmed import PubmedIngestor
from app.ingestors.arxiv import ArxivIngestor

from app.logger import logger

app = FastAPI()

@app.on_event("startup")
def setup():
    logger.info("Starting Ingestor service...")
    db = PostgresDB()
    with db.conn.cursor() as cursor:
        cursor.execute(schema)
    app.state.db = db

@app.get("/ingest/arxiv")
def ingest_arxiv():
    params = {
        "search_query": "cat:cs.AI",
        "start": 0,
        "max_results": 100,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    base_url = "http://export.arxiv.org/api/query?"
    ingestor = ArxivIngestor(app.state.db, params, base_url)
    ingestor.run()
    return {"status": "arxiv_ingested"}

@app.get("/ingest/pubmed")
def ingest_pubmed():
    params = {
        "topic": "AI[All Fields]",
        "max_results": 100,
    }
    ingestor = PubmedIngestor(app.state.db, params=params)
    ingestor.run()
    return {"status": "pubmed_ingested"}

@app.get("/health")
def health():
    return {"status": "ok"}

