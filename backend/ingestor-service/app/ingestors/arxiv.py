import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from app.ingestors.base import AbstractIngestor
from app.db.postgres import PostgresDB
from app.db.schema import papers_schema
from app.models.paper import Paper
from fastapi import FastAPI

from app.logger import logger

# --- Config ---
ARXIV_QUERY = "cat:cs.AI"
MAX_RESULTS = 100

class ArxivIngestor(AbstractIngestor):

    def fetch_documents(self):
        response = requests.get(self.base_url, params=self.params)
        return response.content

    def parse_documents(self, content):
        soup = BeautifulSoup(content, "xml")
        cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(days=self.alert_period)

        entries = soup.find_all("entry")
        results = []
        for entry in entries:
            published = datetime.strptime(entry.published.text, "%Y-%m-%dT%H:%M:%SZ")
            if published < cutoff_date:
                continue

            paper_dict = {
                "source_id": entry.id.text,
                "title": entry.title.text.strip(),
                "summary": entry.summary.text.strip(),
                "link": entry.id.text.strip(),
                "updated": datetime.strptime(entry.updated.text, "%Y-%m-%dT%H:%M:%SZ"),
                "authors": [author.find("name").text for author in entry.find_all("author")],
                "published": published,
                "categories": [c['term'] for c in entry.find_all("category")],
                "source": "arxiv",
            }
            paper = Paper(**paper_dict)
            results.append(paper)
        return results

    def store_documents(self, parsed_data):
        logger.info(f"Parsed {len(parsed_data)} papers")
        for doc in parsed_data:
            logger.info(f"Ingesting document: {doc.title} from Arxiv")
            self.db.insert_document("papers", doc.dict())

if __name__ == "__main__":

    base_url = "http://export.arxiv.org/api/query?"
    params = {
        "search_query": ARXIV_QUERY,
        "start": 0,
        "max_results": MAX_RESULTS,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    db = PostgresDB()
    with db.conn.cursor() as cursor:
        cursor.execute(papers_schema)

    ingestor = ArxivIngestor(db, base_url, params)
    ingestor.run()