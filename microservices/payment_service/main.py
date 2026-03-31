from fastapi import FastAPI, Request, HTTPException
from shared.logging_config import setup_logger
from shared.middleware import RequestContextMiddleware
from shared.log_shipper import ship_log
import random
import asyncio

app = FastAPI(title="payment-service")
app.add_middleware(RequestContextMiddleware)

logger = setup_logger("payment-service")


@app.get("/health")
async def health():
    return {"service": "payment-service", "status": "ok"}


@app.post("/pay")
async def process_payment(request: Request):
    request_id = request.state.request_id
    message = "Payment request received"

    logger.info(
        message,
        extra={
            "service": "payment-service",
            "request_id": request_id,
            "path": "/pay",
            "method": "POST",
            "status_code": 200,
        },
    )
    await ship_log("payment-service", "INFO", message, request_id, "/pay", "POST", 200)

    delay = random.choice([0.1, 0.2, 0.5, 1.5])
    await asyncio.sleep(delay)

    if random.random() < 0.25:
        error_message = "Database timeout while processing payment"

        logger.error(
            error_message,
            extra={
                "service": "payment-service",
                "request_id": request_id,
                "path": "/pay",
                "method": "POST",
                "status_code": 500,
            },
        )
        await ship_log("payment-service", "ERROR", error_message, request_id, "/pay", "POST", 500)
        raise HTTPException(status_code=500, detail="Payment processing failed")

    success_message = "Payment processed successfully"

    logger.info(
        success_message,
        extra={
            "service": "payment-service",
            "request_id": request_id,
            "path": "/pay",
            "method": "POST",
            "status_code": 200,
        },
    )
    await ship_log("payment-service", "INFO", success_message, request_id, "/pay", "POST", 200)

    return {
        "service": "payment-service",
        "status": "success",
        "request_id": request_id,
        "amount": 100
    }