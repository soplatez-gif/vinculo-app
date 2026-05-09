from fastapi import FastAPI
from src.routes import health, webhook

app = FastAPI(title="Vínculo", version="0.1.0")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])


@app.get("/")
async def root():
    return {"app": "Vínculo", "status": "running"}