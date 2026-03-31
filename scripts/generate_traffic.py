import asyncio
import httpx


async def hit_checkout():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://127.0.0.1:8001/checkout", timeout=10.0)
            print(response.status_code, response.text)
        except Exception as exc:
            print("Request failed:", exc)


async def main():
    tasks = [hit_checkout() for _ in range(20)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())