from fastapi import FastAPI, Request, HTTPException
from shared.logging_config import setup_logger
from shared.middleware import RequestContextMiddleware
import httpx

app = FastAPI(title="order-service")
app.add_middleware(RequestContextMiddleware)

logger = setup_logger("order-service")

PAYMENT_SERVICE_URL = "http://127.0.0.1:8003"


@app.get("/health")
async def health():
    return {"service": "order-service", "status": "ok"}


@app.post("/create-order")
async def create_order(request: Request):
    request_id = request.state.request_id

    logger.info(
        "Order creation started",
        extra={
            "service": "order-service",
            "request_id": request_id,
            "path": "/create-order",
            "method": "POST",
            "status_code": 200,
        },
    )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{PAYMENT_SERVICE_URL}/pay",
                headers={"x-request-id": request_id},
            )
            response.raise_for_status()
            payment_result = response.json()

        logger.info(
            "Order created successfully",
            extra={
                "service": "order-service",
                "request_id": request_id,
                "path": "/create-order",
                "method": "POST",
                "status_code": 200,
            },
        )

        return {
            "service": "order-service",
            "status": "order_created",
            "payment": payment_result,
            "request_id": request_id,
        }

    except Exception as exc:
        logger.error(
            f"Order creation failed due to payment-service error: {str(exc)}",
            extra={
                "service": "order-service",
                "request_id": request_id,
                "path": "/create-order",
                "method": "POST",
                "status_code": 500,
            },
        )
        raise HTTPException(status_code=500, detail="Order creation failed")