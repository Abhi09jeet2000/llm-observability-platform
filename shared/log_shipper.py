import httpx
from datetime import datetime


ANOMALY_DETECTOR_URL = "http://127.0.0.1:8004/ingest-log"


async def ship_log(
    service: str,
    level: str,
    message: str,
    request_id: str,
    path: str = None,
    method: str = None,
    status_code: int = None,
):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": service,
        "message": message,
        "request_id": request_id,
        "path": path,
        "method": method,
        "status_code": status_code,
    }

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(ANOMALY_DETECTOR_URL, json=payload)
    except Exception:
        pass