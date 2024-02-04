from typing import Sequence
from app.schemas.token import Token

def get_token() -> Sequence[Token]:
  return [
    Token(
      address="0x55d398326f99059ff775485246999027b3197955",
      name="Tether",
      decimals=6,
      symbol="USDT"
      )
  ]

def get_token_by_address(address: str) -> Token:
  tokens = get_token()

  for token in tokens:
    if token.address == address:
      return token