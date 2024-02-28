from pydantic import BaseModel
from typing import Optional, Sequence

class CreatePresale(BaseModel):
    url: str
    amount: float
    wallets: Sequence[str]
    gas_price: float

class Claim(BaseModel):
    url: str
    wallet: str

class SnipeToken(BaseModel):
    contract: str
    amount: float
    wallets: Sequence[str]
    gas_price: float