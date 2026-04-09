# LLM Observability Platform

**Author:** Abhijeet Raghvendra Kulkarni, Viren Ranjit Kadam  
**Project Type:** Distributed Systems / Observability / LLM-Powered Incident Analysis  
**LLM Used:** Gemini 2.5 Flash-Lite

---

# Overview

`llm-observability-platform` is an end-to-end distributed systems observability project built using multiple Python microservices, structured logging, centralized anomaly detection, incident grouping, and LLM-based incident explanation.

The project simulates a realistic microservice environment where:

- multiple services communicate with each other
- each service emits structured JSON logs
- logs are centralized into an anomaly detection layer
- failures are grouped by `request_id`
- an LLM analyzes the grouped incident and explains likely root cause, propagation path, and recommended next debugging steps

This project is designed to demonstrate how traditional observability techniques can be combined with modern LLM-based reasoning to build an **AI-assisted observability system**.

---

# Why This Project

Modern distributed systems are hard to debug because:

- failures often propagate across multiple services
- one root issue can generate many downstream errors
- logs are noisy and difficult to analyze manually
- traditional monitoring tools show symptoms, but not always likely cause

This project addresses that by combining:

- **structured logging**
- **template-based anomaly detection**
- **request-level incident correlation**
- **LLM-powered incident explanation**

The design follows a practical hybrid approach:

- **Anomaly Detector:** catches suspicious patterns using rolling windows and error bursts
- **LLM Explainer:** explains incidents after they are grouped

This is a better design than using an LLM for every raw log line.

---

# Architecture

## High-Level Flow

```text
Client Request
    |
    v
[user-service] ---> [order-service] ---> [payment-service]
      |                    |                    |
      +--------------------+--------------------+
                           |
                           v
                 [anomaly-detector]
                           |
                           v
                 [incident-explainer]
                           |
                           v
        Gemini 2.5 Flash-Lite Root Cause Explanation
```

---

# Main Components

## 1. Microservices Layer

The project contains 3 FastAPI-based microservices:

### user-service
Responsible for:
- receiving user-facing requests
- handling checkout entry point
- calling `order-service`

### order-service
Responsible for:
- creating orders
- calling `payment-service`

### payment-service
Responsible for:
- processing payments
- simulating latency
- simulating random failures for testing anomaly detection

These services propagate a common `request_id` so that one user request can be traced across all services.

---

## 2. Structured Logging Layer

Each service emits structured JSON logs containing fields like:

- `timestamp`
- `level`
- `service`
- `message`
- `request_id`
- `path`
- `method`
- `status_code`

Example:

```json
{
  "timestamp": "2026-04-09T18:00:00",
  "level": "ERROR",
  "service": "payment-service",
  "message": "Database timeout while processing payment",
  "request_id": "abc-123",
  "path": "/pay",
  "method": "POST",
  "status_code": 500
}
```

This makes logs machine-readable and easy to analyze.

---

## 3. Anomaly Detection Layer

The anomaly detector receives logs from all services and performs:

- log ingestion
- message normalization
- template generation
- rolling-window counting
- burst/spike detection
- request-level incident grouping

### Current anomaly types
- `new_template`
- `error_burst`
- `spike`

### Incident grouping
All logs with the same `request_id` are grouped into one incident record.  
This allows the platform to reconstruct distributed failure chains.

---

## 4. Incident Explainer Layer

The `incident-explainer` service fetches grouped incidents and sends them to **Gemini 2.5 Flash-Lite**.

Gemini then generates:
- short summary
- likely root cause
- propagation path
- blast radius
- recommended debugging steps
- confidence level

This turns raw incidents into human-readable explanations.

---

# Project Structure

```text
.
├── ai_layer/
│   ├── anomaly_detector/
│   │   ├── __init__.py
│   │   └── main.py
│   └── incident_explainer/
│       ├── __init__.py
│       └── main.py
│
├── microservices/
│   ├── user_service/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── order_service/
│   │   ├── __init__.py
│   │   └── main.py
│   └── payment_service/
│       ├── __init__.py
│       └── main.py
│
├── scripts/
│   └── generate_traffic.py
│
├── shared/
│   ├── __init__.py
│   ├── anomaly_store.py
│   ├── gemini_client.py
│   ├── incident_prompt.py
│   ├── log_shipper.py
│   ├── logging_config.py
│   ├── middleware.py
│   ├── normalizer.py
│   └── schemas.py
│
├── requirements.txt
└── README.md
```

---

# How the System Works

## Step 1: A request enters `user-service`
A user sends a checkout request.

## Step 2: `user-service` calls `order-service`
The `request_id` is propagated downstream.

## Step 3: `order-service` calls `payment-service`
The same `request_id` continues across services.

## Step 4: Each service emits structured logs
Logs are printed locally and also shipped to the anomaly detector.

## Step 5: The anomaly detector processes logs
It:
- normalizes messages
- maps them into stable templates
- tracks counts over time
- creates anomalies when thresholds are crossed
- groups logs into incidents by `request_id`

## Step 6: The incident explainer analyzes grouped incidents
If an incident has errors, it is sent to Gemini.

## Step 7: Gemini explains the incident
Gemini returns:
- likely first failing service
- cascade path
- likely cause
- suggested next checks

---

# Installation Guide

This section explains exactly how someone else can set up and run the project.

## Prerequisites

Make sure these are installed:

- Python 3.10 or higher
- pip
- git

You can verify Python:

```bash
python --version
```

or:

```bash
python3 --version
```

---

## 1. Clone the Repository

```bash
git clone https://github.com/Abhi09jeet2000/llm-observability-platform.git
cd llm-observability-platform
```

---

## 2. Create and Activate Virtual Environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install Dependencies

If `requirements.txt` is already present:

```bash
pip install -r requirements.txt
```

If not, install manually:

```bash
pip install fastapi "uvicorn[standard]" httpx python-json-logger pydantic google-genai
```

---

## 4. Set Gemini API Key

This project uses **Gemini 2.5 Flash-Lite** for incident explanation.

You need a valid Gemini API key.

### macOS / Linux

```bash
export GEMINI_API_KEY="your_actual_key_here"
```

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="your_actual_key_here"
```

### Windows CMD

```cmd
set GEMINI_API_KEY=your_actual_key_here
```

### Verify the variable is set

#### macOS / Linux

```bash
echo $GEMINI_API_KEY
```

#### Windows PowerShell

```powershell
echo $env:GEMINI_API_KEY
```

---

# Running the Project

You need to run **5 services** in separate terminals.

Before starting, make sure your virtual environment is activated in each terminal.

---

## Terminal 1: Start anomaly-detector

```bash
uvicorn ai_layer.anomaly_detector.main:app --host 127.0.0.1 --port 8004 --reload
```

---

## Terminal 2: Start payment-service

```bash
uvicorn microservices.payment_service.main:app --host 127.0.0.1 --port 8003 --reload
```

---

## Terminal 3: Start order-service

```bash
uvicorn microservices.order_service.main:app --host 127.0.0.1 --port 8002 --reload
```

---

## Terminal 4: Start user-service

```bash
uvicorn microservices.user_service.main:app --host 127.0.0.1 --port 8001 --reload
```

---

## Terminal 5: Start incident-explainer

Make sure `GEMINI_API_KEY` is set in this terminal first.

```bash
uvicorn ai_layer.incident_explainer.main:app --host 127.0.0.1 --port 8005 --reload
```

---

# Service Ports

| Service | Port |
|--------|------|
| user-service | 8001 |
| order-service | 8002 |
| payment-service | 8003 |
| anomaly-detector | 8004 |
| incident-explainer | 8005 |

---

# Health Check

Run these commands to make sure all services are up:

```bash
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8002/health
curl http://127.0.0.1:8003/health
curl http://127.0.0.1:8004/health
curl http://127.0.0.1:8005/health
```

Expected response:

```json
{"status":"ok"}
```

or similar service-specific JSON.

---

# API Endpoints

## user-service
- `GET /health`
- `GET /profile/{user_id}`
- `POST /checkout`

## order-service
- `GET /health`
- `POST /create-order`

## payment-service
- `GET /health`
- `POST /pay`

## anomaly-detector
- `GET /health`
- `POST /ingest-log`
- `GET /logs`
- `GET /anomalies`
- `GET /incidents`

## incident-explainer
- `GET /health`
- `GET /incidents`
- `GET /explain/{request_id}`
- `GET /explain-latest`

---

# How to Test the Project

## 1. Generate Traffic

Run:

```bash
python scripts/generate_traffic.py
```

This sends multiple checkout requests concurrently.

Because `payment-service` intentionally fails some requests, you should see a mix of:

- `200 OK`
- `500 Checkout failed`

This is expected behavior.

---

## 2. Inspect Collected Logs

```bash
curl http://127.0.0.1:8004/logs | python -m json.tool
```

You should see logs from:
- user-service
- order-service
- payment-service

---

## 3. Inspect Anomalies

```bash
curl http://127.0.0.1:8004/anomalies | python -m json.tool
```

You should see entries like:
- `new_template`
- `error_burst`
- `spike`

---

## 4. Inspect Grouped Incidents

```bash
curl http://127.0.0.1:8004/incidents | python -m json.tool
```

Each incident should contain:
- `request_id`
- `services`
- `error_count`
- `log_count`
- recent errors

---

## 5. Explain Latest Failing Incident with Gemini

```bash
curl http://127.0.0.1:8005/explain-latest | python -m json.tool
```

This should return:
- incident details
- LLM explanation generated by Gemini 2.5 Flash-Lite

---

## 6. Explain a Specific Incident

First inspect incidents and copy a failing `request_id`:

```bash
curl http://127.0.0.1:8004/incidents | python -m json.tool
```

Then run:

```bash
curl http://127.0.0.1:8005/explain/<REQUEST_ID> | python -m json.tool
```

---

# Example Failure Chain

A common simulated failure chain looks like this:

1. `payment-service`
   - `Database timeout while processing payment`
2. `order-service`
   - `Order creation failed due to payment-service error`
3. `user-service`
   - `Checkout failed due to order-service error`

The anomaly detector groups these three logs under the same `request_id`.

The incident explainer then asks Gemini to explain the likely cause and failure propagation.

---

# Example LLM Output

Example explanation:

- Root issue likely originated in `payment-service`
- Payment processing hit a database timeout
- This caused `order-service` to fail order creation
- That failure propagated to `user-service`, resulting in checkout failure
- Recommended next checks:
  - inspect database availability
  - review payment timeout thresholds
  - verify recent deployment changes

---

# Key Design Decisions

## Why not use the LLM on every log line?
Using an LLM for every raw log would be:
- expensive
- slow
- noisy
- hard to scale

So this project uses a **hybrid architecture**:

- anomaly detector handles fast detection
- LLM handles higher-value explanation after grouping

## Why group by `request_id`?
In distributed systems, one root issue causes many downstream symptoms.  
Grouping by `request_id` helps reconstruct the full chain of events across services.

## Why normalize log templates?
Raw logs contain dynamic values like IDs, numbers, and timestamps.  
Normalization lets semantically identical logs map to one template, making anomaly detection more stable.

---

# Technologies Used

- Python
- FastAPI
- Uvicorn
- httpx
- python-json-logger
- Pydantic
- Google GenAI SDK
- Gemini 2.5 Flash-Lite

---

# Current Capabilities

- Multi-service architecture
- Structured JSON logging
- Request context propagation
- Centralized log ingestion
- Template-based anomaly detection
- Rolling-window spike detection
- Incident grouping by request ID
- Gemini-powered incident summarization

---

# Future Improvements

Possible next steps for the project:

- persist logs/anomalies/incidents in SQLite or PostgreSQL
- add OpenTelemetry for traces and metrics
- integrate Grafana, Loki, and Tempo
- build a web dashboard for logs and incidents
- add scenario-based fault injection
- return structured JSON from Gemini instead of plain text
- add service dependency graph visualization
- improve anomaly scoring using statistical baselines

---

# Troubleshooting

## 1. `ModuleNotFoundError`
Always run `uvicorn` commands from the project root.

Correct:

```bash
cd llm-observability-platform
uvicorn microservices.user_service.main:app --port 8001 --reload
```

## 2. All requests fail
Make sure `payment-service` uses:

```python
await asyncio.sleep(delay)
```

and not:

```python
time.sleep(delay)
```

## 3. Gemini explanation fails
Check:
- API key is valid
- environment variable is set
- internet connection is working
- model name is correct

## 4. No incidents are returned
Generate more traffic first:

```bash
python scripts/generate_traffic.py
```

## 5. No anomalies detected
You may need to generate more load so thresholds are crossed.

---

# Who This Project Is For

This project is useful for:

- engineers learning observability design
- developers experimenting with LLM-assisted SRE workflows
- building a portfolio project around AI + systems
- to solve production issues
- to reduce time required for developer to find bugs

---

# Author

GitHub: [Abhi09jeet2000](https://github.com/Abhi09jeet2000)

---

# License

Add a license here if you want to make the project open source for reuse.
