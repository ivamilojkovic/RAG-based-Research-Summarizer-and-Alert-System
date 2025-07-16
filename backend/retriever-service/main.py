import pika
import json
from retriever import retrieve_relevant_chunks
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RetrieveRequest(BaseModel):
    alert_id: str
    query: str = "Show me the most relevant AI papers related to genomics"
    top_k: int = 5

def send_summarization_job(alert_id, prompt, chunks):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",
            credentials=pika.PlainCredentials("user", "password")
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="summarization_jobs", durable=True)
    summarization_job = {
        "alert_id": alert_id,
        "prompt": prompt,
        "chunks": chunks
    }
    channel.basic_publish(
        exchange='',
        routing_key='summarization_jobs',
        body=json.dumps(summarization_job),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

@app.post("/retrieve/")
def retrieve(request: RetrieveRequest):
    results = retrieve_relevant_chunks(query=request.query, top_k=request.top_k)
    
    if not results:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")
    
    chunks = [r["text"] for r in results]
    send_summarization_job(request.alert_id, request.query, chunks)
    
    return {
        "message": "Retrieval successful, summarization job sent.",
        "retrieved_chunks": len(results),
        "chunks_preview": [c[:150] + "..." for c in chunks]
    }