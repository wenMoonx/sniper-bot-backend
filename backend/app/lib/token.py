from typing import Sequence
from app.schemas.token import Token


def get_token() -> Sequence[Token]:
    return [
        Token(
            address="0x7ef95a0FEE0Dd31b22626fA2e10Ee6A223F8a684",
            name="Tether",
            decimals=6,
            symbol="USDT"
        ),
        Token(
            address="0x78867BbEeF44f2326bF8DDd1941a4439382EF2A7",
            # address="0x78867BbEeF44f2326bF8DDd1941a4439382EF2A6",
            name="BUSD",
            decimals=18,
            symbol="BUSD"
        )
    ]


def get_token_by_address(address: str) -> Token:
    tokens = get_token()

    for token in tokens:
        if token.address.lower() == address.lower():
            return token
