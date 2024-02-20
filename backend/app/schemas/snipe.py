from pydantic import BaseModel
from typing import Optional

class CreatePresale(BaseModel):
    url: str
    amount: float
    wallet: str

class Claim(BaseModel):
    url: str
    wallet: str