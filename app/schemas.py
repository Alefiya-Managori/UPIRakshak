from pydantic import BaseModel
from typing import Optional

class TransactionBase(BaseModel):
    user_id: str
    amount: float
    location: str
    device_id: str
    typing_speed: float
    is_senior: int  # 1 for Yes, 0 for No

class TransactionResponse(BaseModel):
    decision: str
    risk_score: float
    reason: Optional[str] = None