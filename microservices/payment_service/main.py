from fastapi import FastAPI, Request, HTTPException
from shared.logging_config import setup_logger
from shared.middleware import RequestContextMiddleware
import random
import time

app = FastAPI(title="payment-service")
app.add_middleware(RequestContextMiddleware)

logger = setup_logger("payment-service")


@app.get("/health")
async def health():
    return {"service": "payment-service", "status": "ok"}


@app.post("/pay")
async def process_payment(request: Request):
    request_id = request.state.request_id

    logger.info(
        "Payment request received",
        extra={
            "service": "payment-service",
            "request_id": request_id,
            "path": "/pay",
            "method": "POST",
            "status_code": 200,
        },
    )

    # Simulate occasional latency
    delay = random.choice([0.1, 0.2, 0.5, 1.5])
    time.sleep(delay)

    # Simulate anomaly / failure sometimes
    if random.random() < 0.25:
        logger.error(
            "Database timeout while processing payment",
            extra={
                "service": "payment-service",
                "request_id": request_id,
                "path": "/pay",
                "method": "POST",
                "status_code": 500,
            },
        )
        raise HTTPException(status_code=500, detail="Payment processing failed")

    logger.info(
        "Payment processed successfully",
        extra={
            "service": "payment-service",
            "request_id": request_id,
            "path": "/pay",
            "method": "POST",
            "status_code": 200,
        },
    )

    return {
        "service": "payment-service",
        "status": "success",
        "request_id": request_id,
        "amount": 100
    }