from collections import deque, defaultdict
from datetime import datetime, timedelta

LOG_HISTORY = deque(maxlen=10000)
ANOMALIES = []
INCIDENTS = {}

# Per (service, template_key) -> list of timestamps
TEMPLATE_WINDOWS = defaultdict(deque)

# Per request_id -> list of logs
REQUEST_GROUPS = defaultdict(list)

# Track first seen template
TEMPLATE_FIRST_SEEN = {}

# Dedup anomaly creation
LAST_ANOMALY_AT = {}

WINDOW_SECONDS = 60


def add_log(log):
    LOG_HISTORY.append(log)


def get_logs():
    return list(LOG_HISTORY)


def add_anomaly(anomaly):
    ANOMALIES.append(anomaly)


def get_anomalies():
    return ANOMALIES


def get_incidents():
    return INCIDENTS


def add_to_request_group(request_id, log):
    REQUEST_GROUPS[request_id].append(log)


def get_request_group(request_id):
    return REQUEST_GROUPS.get(request_id, [])


def add_to_template_window(service, template_key, ts):
    key = (service, template_key)
    TEMPLATE_WINDOWS[key].append(ts)

    cutoff = ts - timedelta(seconds=WINDOW_SECONDS)
    while TEMPLATE_WINDOWS[key] and TEMPLATE_WINDOWS[key][0] < cutoff:
        TEMPLATE_WINDOWS[key].popleft()


def get_template_window_count(service, template_key):
    return len(TEMPLATE_WINDOWS[(service, template_key)])


def set_first_seen(service, template_key, ts):
    key = (service, template_key)
    if key not in TEMPLATE_FIRST_SEEN:
        TEMPLATE_FIRST_SEEN[key] = ts


def get_first_seen(service, template_key):
    return TEMPLATE_FIRST_SEEN.get((service, template_key))


def should_emit_anomaly(service, template_key, anomaly_type, ts, cooldown_seconds=30):
    key = (service, template_key, anomaly_type)
    last_ts = LAST_ANOMALY_AT.get(key)

    if last_ts is None or (ts - last_ts).total_seconds() > cooldown_seconds:
        LAST_ANOMALY_AT[key] = ts
        return True
    return False


def create_or_update_incident(request_id, log):
    if request_id not in INCIDENTS:
        INCIDENTS[request_id] = {
            "request_id": request_id,
            "services": set(),
            "errors": [],
            "logs": [],
            "first_seen": log["timestamp"],
            "last_seen": log["timestamp"],
        }

    incident = INCIDENTS[request_id]
    incident["services"].add(log["service"])
    incident["logs"].append(log)
    incident["last_seen"] = log["timestamp"]

    if log["level"].upper() == "ERROR":
        incident["errors"].append(log)


def serialize_incidents():
    result = []
    for request_id, incident in INCIDENTS.items():
        result.append({
            "request_id": request_id,
            "services": list(incident["services"]),
            "error_count": len(incident["errors"]),
            "log_count": len(incident["logs"]),
            "first_seen": incident["first_seen"],
            "last_seen": incident["last_seen"],
            "errors": incident["errors"][-5:],
        })
    return result