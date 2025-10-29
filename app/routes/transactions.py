from fastapi import APIRouter, HTTPException
from app.db import collection

router = APIRouter()

@router.get("/v1/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    doc = await collection.find_one({"_id": transaction_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    doc["transaction_id"] = doc["_id"]
    del doc["_id"]
    return doc
