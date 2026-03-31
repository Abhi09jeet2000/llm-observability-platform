from fastapi import FastAPI, Request, HTTPException
from shared.logging_config import setup_logger
from shared.middleware import RequestContextMiddleware
import httpx

app = FastAPI(title="user-service")
app.add_middleware(RequestContextMiddleware)

logger = setup_logger("user-service")

ORDER_SERVICE_URL = "http://127.0.0.1:8002"


@app.get("/health")
async def health():
    return {"service": "user-service", "status": "ok"}


@app.get("/profile/{user_id}")
async def get_profile(user_id: int, request: Request):
    request_id = request.state.request_id

    logger.info(
        f"Fetching profile for user {user_id}",
        extra={
            "service": "user-service",
            "request_id": request_id,
            "path": f"/profile/{user_id}",
            "method": "GET",
            "status_code": 200,
        },
    )

    return {
        "service": "user-service",
        "user_id": user_id,
        "name": f"user-{user_id}",
        "request_id": request_id,
    }


@app.post("/checkout")
async def checkout(request: Request):
    request_id = request.state.request_id

    logger.info(
        "Checkout started",
        extra={
            "service": "user-service",
            "request_id": request_id,
            "path": "/checkout",
            "method": "POST",
            "status_code": 200,
        },
    )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{ORDER_SERVICE_URL}/create-order",
                headers={"x-request-id": request_id},
            )
            response.raise_for_status()
            order_result = response.json()

        logger.info(
            "Checkout completed successfully",
            extra={
                "service": "user-service",
                "request_id": request_id,
                "path": "/checkout",
                "method": "POST",
                "status_code": 200,
            },
        )

        return {
            "service": "user-service",
            "status": "checkout_success",
            "order": order_result,
            "request_id": request_id,
        }

    except Exception as exc:
        logger.error(
            f"Checkout failed due to order-service error: {str(exc)}",
            extra={
                "service": "user-service",
                "request_id": request_id,
                "path": "/checkout",
                "method": "POST",
                "status_code": 500,
            },
        )
        raise HTTPException(status_code=500, detail="Checkout failed")