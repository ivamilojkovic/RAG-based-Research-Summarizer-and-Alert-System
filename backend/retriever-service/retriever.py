from qdrant_client import QdrantClient
from qdrant_client.models import Filter, SearchParams, PointStruct, FieldCondition, MatchValue, Range
from sentence_transformers import SentenceTransformer
import os, datetime

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")

client = QdrantClient(
    host=os.getenv("QDRANT_HOST", "qdrant"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)

def retrieve_relevant_chunks(query, top_k=5):
    query_vector = embed_text(query)
    period = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    timestamp = period.timestamp()

    # Filtering using metadata
    filters = Filter(
        must=[
            FieldCondition(key="published_timestamp", range=Range(gte=timestamp)),
        ]
    )
    results = client.search(
        collection_name="papers",
        query_vector=query_vector,
        limit=top_k,
        query_filter=filters,
        with_payload=True
    )
    return [
        {
            "title": r.payload.get("title"),
            "source": r.payload.get("source"),
            "link": r.payload.get("link"),
            "published": r.payload.get("published"),
            "text": r.payload["text"], 
            "score": r.score
        } for r in results
    ]

def embed_text(text):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    vector_dim = model.get_sentence_embedding_dimension()
    print(f"Embedding size: {vector_dim}")

    text_vector = model.encode(text)
    return text_vector

