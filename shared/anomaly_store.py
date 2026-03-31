from collections import defaultdict, deque
from datetime import datetime, timedelta

LOG_HISTORY = deque(maxlen=5000)
ANOMALIES = []

TEMPLATE_COUNTS = defaultdict(int)
TEMPLATE_FIRST_SEEN = {}
TEMPLATE_REQUEST_IDS = defaultdict(list)


def add_log(log):
    LOG_HISTORY.append(log)


def get_logs():
    return list(LOG_HISTORY)


def add_anomaly(anomaly):
    ANOMALIES.append(anomaly)


def get_anomalies():
    return ANOMALIES