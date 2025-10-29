from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransactionIn(BaseModel):
    transaction_id: str = Field(..., alias="transaction_id")
    source_account: str
    destination_account: str
    amount: float
    currency: str

class TransactionOut(TransactionIn):
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
