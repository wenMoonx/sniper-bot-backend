from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    address: str
    name: str
    decimals: int
    symbol: str

class TransferEth(BaseModel):
    wallet: str
    amount: float
    receiver: str

class TokenTransfer(TransferEth):
    token: str

class Swap(BaseModel):
    wallet: str
    src_token: Optional[str]
    dst_token: Optional[str]
    amount: float