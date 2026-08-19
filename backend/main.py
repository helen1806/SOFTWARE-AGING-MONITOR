from fastapi import FastAPI
from tasks import perform_health_check

app = FastAPI(title="Software Aging Monitor API")

@app.post("/trigger-test-check")
def trigger_test_check(url: str):
    perform_health_check.delay(website_id=999, url=url)
    return {"message": f"Health check queued for {url}"}
