from pydantic import BaseModel

class Token(BaseModel):
    address: str
    name: str
    decimals: int
    symbol: str

class TokenTransfer(BaseModel):
    wallet: str
    token: str
    amount: int
    receiver: str

class Swap(BaseModel):
    wallet: str
    src_token: str
    dst_token: str
    amount: int