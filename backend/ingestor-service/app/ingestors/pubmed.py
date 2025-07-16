from datetime import datetime, timedelta, timezone
from app.ingestors.base import AbstractIngestor
from app.db.postgres import PostgresDB, schema
import os
import metapub, time
from metapub import PubMedFetcher
from app.models.paper import Paper

from app.logger import logger

# --- Config ---
TOPIC = "AI[All Fields]"
MAX_RESULTS = 100

def extract_relevant_dates(history):
    history_map = dict(history or [])
    published = (
        history_map.get("pubmed") or
        history_map.get("entrez") or
        history_map.get("aheadofprint") or
        history_map.get("accepted")
    )
    updated = history_map.get("revised")
    return published, updated

class PubmedIngestor(AbstractIngestor):
    def fetch_documents(self):
        self.today = datetime.now(timezone.utc)
        self.cutoff_date = (self.today - timedelta(days=7)).strftime("%Y/%m/%d")

        metapub.config.ncbi_api_key=os.getenv("NCBI_API_KEY")

        self.fetcher = PubMedFetcher()
        pmids = self.fetcher.pmids_for_query(
            f"{TOPIC}[Title/Abstract] AND ({self.cutoff_date}[PDAT] : {self.today.strftime('%Y/%m/%d')}[PDAT])",
            sort="pub+date",
            retmax=MAX_RESULTS)
        if not pmids:
            print("No IDs found.")

        return pmids

    def parse_documents(self, pmids):
        results = []
        for pmid in pmids:
            try:
                article = self.fetcher.article_by_pmid(pmid)
                if article is None:
                    continue

                # filtered_attrs = {k: v for k, v in vars(article).items() if isinstance(v, (str, int, list, dict, type(None)))}
                # pprint(filtered_attrs)
            
                published_date, updated_date = extract_relevant_dates(getattr(article, "history", None))
                if published_date is None:
                    published_date = self.today

                paper_dict = {
                    "source_id": article.pmid,
                    "title": article.title or "",
                    "summary": article.abstract or "",
                    "link": f"https://pubmed.ncbi.nlm.nih.gov/{article.pmid}/",
                    "updated": updated_date,
                    "authors": article.authors if article.authors else [],
                    "published": published_date,
                    "categories": [],
                    "source": "pubmed"
                }
                paper = Paper(**paper_dict)
                results.append(paper)

            except Exception as e:
                logger.error(f"Error processing PMID {pmid}: {e}")
                
                time.sleep(0.5)
    
        return results

    def store_documents(self, parsed_data):
        logger.info(f"Parsed {len(parsed_data)} papers from Pubmed")
        for doc in parsed_data:
            self.db.insert_document("papers", doc.dict())

if __name__ == "__main__":
    db = PostgresDB()
    with db.conn.cursor() as cursor:
        cursor.execute(schema)

    ingestor = PubmedIngestor(db)
    ingestor.run()