import asyncio
import httpx


async def hit_checkout(i: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://127.0.0.1:8001/checkout", timeout=15.0)
            print(f"{i}: {response.status_code} {response.text}")
        except Exception as exc:
            print(f"{i}: Request failed: {exc}")


async def main():
    tasks = [hit_checkout(i) for i in range(10)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())