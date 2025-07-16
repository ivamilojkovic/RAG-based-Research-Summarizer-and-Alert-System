from abc import ABC, abstractmethod

class AbstractIngestor(ABC):
    """
    Abstract base class for all ingestors.
    """
    def __init__(self, db, params, base_url=None):
        self.db = db
        self.base_url = base_url
        self.params = params

    @abstractmethod
    def fetch_documents(self):
        pass

    @abstractmethod
    def parse_documents(self, raw_data):
        pass

    @abstractmethod
    def store_documents(self, parsed_data):
        pass

    def run(self):
        raw = self.fetch_documents()
        parsed = self.parse_documents(raw)
        self.store_documents(parsed)
