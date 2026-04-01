from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
import httpx
from shared.gemini_client import get_gemini_client, MODEL_NAME
from shared.incident_prompt import build_incident_prompt

app = FastAPI(title="incident-explainer")

ANOMALY_DETECTOR_INCIDENTS_URL = "http://127.0.0.1:8004/incidents"


@app.get("/health")
async def health():
    return {"service": "incident-explainer", "status": "ok", "model": MODEL_NAME}


@app.get("/incidents")
async def get_incidents():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ANOMALY_DETECTOR_INCIDENTS_URL)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch incidents: {str(exc)}")


@app.get("/explain/{request_id}")
async def explain_incident(request_id: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ANOMALY_DETECTOR_INCIDENTS_URL)
            response.raise_for_status()
            incidents = response.json().get("incidents", [])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch incidents: {str(exc)}")

    matching = None
    for incident in incidents:
        if incident.get("request_id") == request_id:
            matching = incident
            break

    if not matching:
        raise HTTPException(status_code=404, detail="Incident not found")

    if matching.get("error_count", 0) == 0:
        return {
            "request_id": request_id,
            "message": "This incident has no errors. Skipping LLM explanation.",
            "incident": matching,
        }

    prompt = build_incident_prompt(matching)

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        explanation_text = getattr(response, "text", None)
        if not explanation_text:
            explanation_text = str(response)

        return {
            "request_id": request_id,
            "model": MODEL_NAME,
            "incident": matching,
            "explanation": explanation_text,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gemini explanation failed: {str(exc)}")


@app.get("/explain-latest")
async def explain_latest_failing_incident():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ANOMALY_DETECTOR_INCIDENTS_URL)
            response.raise_for_status()
            incidents = response.json().get("incidents", [])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch incidents: {str(exc)}")

    failing_incidents = [i for i in incidents if i.get("error_count", 0) > 0]
    if not failing_incidents:
        return {"message": "No failing incidents available to explain."}

    latest = sorted(
        failing_incidents,
        key=lambda x: x.get("last_seen", ""),
        reverse=True
    )[0]

    prompt = build_incident_prompt(latest)

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        explanation_text = getattr(response, "text", None)
        if not explanation_text:
            explanation_text = str(response)

        return {
            "request_id": latest["request_id"],
            "model": MODEL_NAME,
            "incident": latest,
            "explanation": explanation_text,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gemini explanation failed: {str(exc)}")