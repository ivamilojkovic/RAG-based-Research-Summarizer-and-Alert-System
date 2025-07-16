from pydantic import BaseModel

class AlertRequest(BaseModel):
    query: str
    period: int