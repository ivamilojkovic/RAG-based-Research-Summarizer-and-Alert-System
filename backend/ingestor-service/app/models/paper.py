# shared/models/paper.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Paper(BaseModel):
    source_id: str
    source: str
    title: Optional[str]
    summary: Optional[str]
    link: Optional[str]
    published: Optional[datetime]
    updated: Optional[datetime]
    authors: Optional[List[str]] = []
    categories: Optional[List[str]] = []
