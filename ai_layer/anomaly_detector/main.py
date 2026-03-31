from fastapi import FastAPI
from datetime import datetime
from shared.schemas import LogEvent, AnomalyEvent
from shared.normalizer import normalize_message, generate_template_key
from shared.anomaly_store import (
    add_log,
    get_logs,
    add_anomaly,
    get_anomalies,
    TEMPLATE_COUNTS,
    TEMPLATE_FIRST_SEEN,
    TEMPLATE_REQUEST_IDS,
)

app = FastAPI(title="anomaly-detector")


@app.get("/health")
async def health():
    return {"service": "anomaly-detector", "status": "ok"}


@app.post("/ingest-log")
async def ingest_log(log: LogEvent):
    normalized_message = normalize_message(log.message)
    template_key = generate_template_key(normalized_message)

    log_record = {
        "timestamp": log.timestamp,
        "level": log.level,
        "service": log.service,
        "message": log.message,
        "normalized_message": normalized_message,
        "template_key": template_key,
        "request_id": log.request_id,
        "path": log.path,
        "method": log.method,
        "status_code": log.status_code,
    }

    add_log(log_record)

    TEMPLATE_COUNTS[(log.service, template_key)] += 1
    TEMPLATE_REQUEST_IDS[(log.service, template_key)].append(log.request_id)

    if (log.service, template_key) not in TEMPLATE_FIRST_SEEN:
        TEMPLATE_FIRST_SEEN[(log.service, template_key)] = datetime.utcnow()

        anomaly = AnomalyEvent(
            anomaly_type="new_template",
            service=log.service,
            message=normalized_message,
            template_key=template_key,
            count=TEMPLATE_COUNTS[(log.service, template_key)],
            level=log.level,
            request_ids=TEMPLATE_REQUEST_IDS[(log.service, template_key)][-5:],
        )
        add_anomaly(anomaly.dict())

    if log.level.upper() == "ERROR":
        count = TEMPLATE_COUNTS[(log.service, template_key)]

        if count >= 3:
            anomaly = AnomalyEvent(
                anomaly_type="repeated_error",
                service=log.service,
                message=normalized_message,
                template_key=template_key,
                count=count,
                level=log.level,
                request_ids=TEMPLATE_REQUEST_IDS[(log.service, template_key)][-5:],
            )
            add_anomaly(anomaly.dict())

    return {
        "status": "ingested",
        "template_key": template_key,
        "normalized_message": normalized_message,
    }


@app.get("/logs")
async def logs():
    return {"logs": get_logs()}


@app.get("/anomalies")
async def anomalies():
    return {"anomalies": get_anomalies()}