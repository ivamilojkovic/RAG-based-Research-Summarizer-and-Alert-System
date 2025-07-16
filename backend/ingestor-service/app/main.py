from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db.postgres import PostgresDB
from app.db.schema import papers_schema, alerts_schema
from app.ingestors.pubmed import PubmedIngestor
from app.ingestors.arxiv import ArxivIngestor
from app.models.alert import AlertRequest
import asyncio
from uuid import uuid4
from datetime import datetime

from app.logger import logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def setup():
    logger.info("Starting Ingestor service...")
    db = PostgresDB()
    with db.conn.cursor() as cursor:
        cursor.execute(papers_schema)
        cursor.execute(alerts_schema)
    app.state.db = db

@app.post("/create-alert")
async def start_ingestion(request: AlertRequest):
    alert_id = str(uuid4())
    logger.info(f"Received ingestion request: query={request.query}, period={request.period}, id={alert_id}")

    try:
        # Store alert with status 'pending'
        with app.state.db.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO alerts (id, query, period, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (alert_id, request.query, request.period, "pending", datetime.utcnow())
            )
            app.state.db.conn.commit()

        async def run_arxiv():
            params = {
                "search_query": "cat:cs.AI",
                "start": 0,
                "max_results": 100,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
            base_url = "http://export.arxiv.org/api/query?"
            ingestor = ArxivIngestor(app.state.db, params, base_url, user_query=request.query, period=request.period)
            ingestor.run()

        async def run_pubmed():
            params = {
                "topic": "AI[All Fields]",
                "max_results": 100,
            }
            ingestor = PubmedIngestor(app.state.db, params=params, base_url=None, user_query=request.query, period=request.period)
            ingestor.run()

        # Run both in parallel
        asyncio.create_task(run_arxiv())
        asyncio.create_task(run_pubmed())

        return {"alert_id": alert_id, "status": "pending"}

    except Exception as e:
        logger.error(f"Failed to create alert: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/get-alerts")
async def get_alerts():
    try:
        db = PostgresDB()
        with db.conn.cursor() as cursor:
            cursor.execute("SELECT id, query, period, status FROM alerts ORDER BY created_at DESC")
            rows = cursor.fetchall()
            alerts = [
                {"id": row[0], "query": row[1], "period": row[2], "status": row[3]}
                for row in rows
            ]
            return alerts
    except Exception as e:
        print("Error fetching alerts:", e)
        return {"error": "Failed to fetch alerts"}

@app.get("/health")
async def health():
    return {"status": "ok"}

