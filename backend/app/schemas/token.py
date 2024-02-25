from pydantic import BaseModel
from typing import Optional, Sequence

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
    gas_price: float

class MultiSwap(BaseModel):
    wallets: Sequence[str]
    src_token: Optional[str]
    dst_token: Optional[str]
    amount_type: int
    gas_price: float

class MultiTransferEth(BaseModel):
    wallets: Sequence[str]
    amount_type: int
    receiver: str

class MultiTokenTransfer(MultiTransferEth):
    token: str

class Tx(BaseModel):
    sender: str
    receiver: str
    value: str