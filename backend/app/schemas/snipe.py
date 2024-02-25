from pydantic import BaseModel
from typing import Optional

class CreatePresale(BaseModel):
    url: str
    amount: float
    wallet: str
    gas_price: float

class Claim(BaseModel):
    url: str
    wallet: str