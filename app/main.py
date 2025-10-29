from fastapi import FastAPI
from app.routes import webhook, transactions, health

app = FastAPI(title="Transaction Webhook Service")

app.include_router(health.router)
app.include_router(webhook.router)
app.include_router(transactions.router)
