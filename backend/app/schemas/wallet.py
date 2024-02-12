from pydantic import BaseModel

class PayFee(BaseModel):
    wallet_address: str 
