from pydantic import BaseModel
from typing import Dict, Any

class ServiceStatus(BaseModel):
    name: str
    status: str
    latency_ms: int | None = None
    details: Dict[str, Any] = {}
