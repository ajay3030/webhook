from fastapi import APIRouter, status
from datetime import datetime
from app.schemas import TransactionIn
from app.db import collection
from app.queue import publish_transaction

router = APIRouter()

@router.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED)
async def receive_transaction(payload: TransactionIn):
    existing = await collection.find_one({"_id": payload.transaction_id})
    if existing:
        # Idempotent behavior — don’t reprocess
        return {"message": "Duplicate transaction ignored"}

    # Insert new transaction as PROCESSING
    doc = {
        "_id": payload.transaction_id,
        "source_account": payload.source_account,
        "destination_account": payload.destination_account,
        "amount": payload.amount,
        "currency": payload.currency,
        "status": "PROCESSING",
        "created_at": datetime.utcnow(),
        "processed_at": None,
    }
    await collection.insert_one(doc)

    # Push to RabbitMQ for background processing
    publish_transaction(payload.transaction_id)

    return {"message": "Transaction accepted for processing"}
