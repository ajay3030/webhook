from fastapi import FastAPI
from app.routes import webhook, transactions, health
from app.worker_manager import worker_manager

app = FastAPI(title="Transaction Webhook Service")

@app.on_event("startup")
async def startup_event():
    """Start background worker when API starts"""
    worker_manager.start_worker_thread()

app.include_router(health.router)
app.include_router(webhook.router)
app.include_router(transactions.router)
