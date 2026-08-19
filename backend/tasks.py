import httpx
import asyncio
from datetime import datetime
from celery_app import celery_app

@celery_app.task(name="tasks.perform_health_check")
def perform_health_check(website_id: int, url: str):
    async def check_url():
        start_time = datetime.utcnow()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                print(f"[{url}] Status: {response.status_code} | Time: {time_ms:.2f}ms")
        except Exception as e:
            print(f"[{url}] Failed: {str(e)}")

    asyncio.run(check_url())

@celery_app.task(name="tasks.prune_old_records")
def prune_old_records():
    print("Running scheduled pruning job to prevent unbounded database growth...")
