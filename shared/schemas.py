from pydantic import BaseModel
from typing import Optional, List


class LogEvent(BaseModel):
    timestamp: str
    level: str
    service: str
    message: str
    request_id: str
    path: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None


class AnomalyEvent(BaseModel):
    anomaly_type: str
    service: str
    message: str
    template_key: str
    count: int
    level: str
    request_ids: List[str]