from pydantic import BaseModel

class RegisterUser(BaseModel):
    email: str
    username: str
    password: str

class LoginUser(BaseModel):
    signature: str
    publicAddress: str
    nonce: int
