from fastapi import FastAPI
from datetime import datetime
from shared.schemas import LogEvent, AnomalyEvent
from shared.normalizer import normalize_message, generate_template_key
from shared.anomaly_store import (
    add_log,
    get_logs,
    add_anomaly,
    get_anomalies,
    add_to_request_group,
    add_to_template_window,
    get_template_window_count,
    set_first_seen,
    get_first_seen,
    should_emit_anomaly,
    create_or_update_incident,
    serialize_incidents,
    WINDOW_SECONDS,
)

app = FastAPI(title="anomaly-detector")


SPIKE_THRESHOLD = 8
ERROR_BURST_THRESHOLD = 3


@app.get("/health")
async def health():
    return {"service": "anomaly-detector", "status": "ok"}


@app.post("/ingest-log")
async def ingest_log(log: LogEvent):
    normalized_message = normalize_message(log.message)
    template_key = generate_template_key(normalized_message)
    ts = datetime.fromisoformat(log.timestamp)

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
    add_to_request_group(log.request_id, log_record)
    create_or_update_incident(log.request_id, log_record)

    add_to_template_window(log.service, template_key, ts)
    current_count = get_template_window_count(log.service, template_key)

    first_seen = get_first_seen(log.service, template_key)
    if first_seen is None:
        set_first_seen(log.service, template_key, ts)

        anomaly = AnomalyEvent(
            anomaly_type="new_template",
            service=log.service,
            message=normalized_message,
            template_key=template_key,
            count=current_count,
            level=log.level,
            request_ids=[log.request_id],
            window_seconds=WINDOW_SECONDS,
            reason="First time this normalized template was seen for this service.",
        )
        add_anomaly(anomaly.model_dump())

    if current_count >= SPIKE_THRESHOLD and should_emit_anomaly(log.service, template_key, "spike", ts):
        anomaly = AnomalyEvent(
            anomaly_type="spike",
            service=log.service,
            message=normalized_message,
            template_key=template_key,
            count=current_count,
            level=log.level,
            request_ids=[log.request_id],
            window_seconds=WINDOW_SECONDS,
            reason=f"Template appeared {current_count} times in the last {WINDOW_SECONDS} seconds.",
        )
        add_anomaly(anomaly.model_dump())

    if log.level.upper() == "ERROR" and current_count >= ERROR_BURST_THRESHOLD:
        if should_emit_anomaly(log.service, template_key, "error_burst", ts):
            anomaly = AnomalyEvent(
                anomaly_type="error_burst",
                service=log.service,
                message=normalized_message,
                template_key=template_key,
                count=current_count,
                level=log.level,
                request_ids=[log.request_id],
                window_seconds=WINDOW_SECONDS,
                reason=f"Error template repeated {current_count} times in the last {WINDOW_SECONDS} seconds.",
            )
            add_anomaly(anomaly.model_dump())

    return {
        "status": "ingested",
        "template_key": template_key,
        "normalized_message": normalized_message,
        "window_count": current_count,
    }


@app.get("/logs")
async def logs():
    return {"logs": get_logs()}


@app.get("/anomalies")
async def anomalies():
    return {"anomalies": get_anomalies()}


@app.get("/incidents")
async def incidents():
    return {"incidents": serialize_incidents()}