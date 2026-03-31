import json


def build_incident_prompt(incident: dict) -> str:
    compact_incident = {
        "request_id": incident.get("request_id"),
        "services": incident.get("services", []),
        "error_count": incident.get("error_count", 0),
        "log_count": incident.get("log_count", 0),
        "first_seen": incident.get("first_seen"),
        "last_seen": incident.get("last_seen"),
        "errors": incident.get("errors", []),
    }

    return f"""
You are an SRE incident analysis assistant.

Analyze this distributed-systems incident and produce:
1. A short summary (2-4 sentences)
2. Most likely root cause
3. Failure propagation path across services
4. Blast radius
5. Recommended next debugging steps (3 bullets max)
6. Confidence level: High / Medium / Low

Rules:
- Be concise and technical.
- Base your answer only on the provided incident data.
- If uncertain, say so clearly.
- Prefer identifying the earliest likely failing service.

Incident JSON:
{json.dumps(compact_incident, indent=2)}
""".strip()