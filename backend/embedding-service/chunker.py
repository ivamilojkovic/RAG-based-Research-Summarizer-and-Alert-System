import psycopg2
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, CollectionStatus
import os
import mlflow
import uuid
from datetime import datetime

# Setup
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
qdrant = QdrantClient(host="qdrant")
COLLECTION = "papers"

# Create collection if needed
try:
    qdrant.get_collection(COLLECTION)
except Exception:
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

def process_document(source, source_id):
    # fetch metadata & summary from Postgres
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT title, summary, published, link FROM papers WHERE source=%s AND source_id=%s",
        (source, source_id)
    )
    result = cur.fetchone()
    conn.close()

    if result is None:
        print("Document not found")
        return

    title, summary, published, link = result
    title = title.strip() if title else ""
    summary = summary.strip() if summary else ""

    title_chunk = chunk_text(title, chunk_size=50, overlap=0)[0] if title else ""

    # If no summary, return only the title chunk
    if not summary:
        return [title_chunk]

    summary_chunks = chunk_text(summary, chunk_size=300, overlap=100)

    # Combine title with each summary chunk
    combined_chunks = [f"{title_chunk}\n\n{chunk}" for chunk in summary_chunks]
    print(f"Inserting {len(combined_chunks)} vectors for {source_id}")

    vectors = model.encode(combined_chunks).tolist()

    points = []
    for i, (vec, text) in enumerate(zip(vectors, combined_chunks)):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                "source": source,
                "source_id": source_id,
                "chunk_index": i,
                "text": text,
                "title": title,
                "link": link,
                "published_timestamp": published.timestamp()
            }
        ))

    qdrant.upsert(collection_name=COLLECTION, points=points)
    print(f"[✓] Embedded and uploaded {len(points)} chunks")

def chunk_text(text, chunk_size=300, overlap=100):

    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i+chunk_size]
        chunks.append(" ".join(chunk))
    return chunks
