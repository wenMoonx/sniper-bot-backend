from pydantic import BaseModel
from typing import Optional

class CreatePresale(BaseModel):
    presale_contract: str
    token: str
    amount: float
    wallet: str

class Claim(BaseModel):
    presale_contract: str
    wallet: str