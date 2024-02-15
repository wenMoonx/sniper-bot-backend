from typing import Sequence
from app.schemas.token import Token
from app.core.conf import settings

tokens = {
    97: [
        Token(
            address="0x7ef95a0FEE0Dd31b22626fA2e10Ee6A223F8a684",
            name="Tether",
            decimals=6,
            symbol="USDT"
        ),
        Token(
            address="0x78867BbEeF44f2326bF8DDd1941a4439382EF2A7",
            name="BUSD",
            decimals=18,
            symbol="BUSD"
        ),
    ],
    56: [
        Token(
            address="0x63b7e5aE00cc6053358fb9b97B361372FbA10a5e",
            name="Tether",
            decimals=6,
            symbol="USDT"
        ),
        Token(
            address="0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
            name="BUSD",
            decimals=18,
            symbol="BUSD"
        ),
        Token(
            address="0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
            name="Cake",
            decimals=18,
            symbol="Cake"
        )
    ]
}

wbnb = {
    97: Token(
            address="0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",
            name="WBNB",
            decimals=18,
            symbol="WBNB"
        ),
    56: Token(
            address="0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
            name="WBNB",
            decimals=18,
            symbol="WBNB"
        )
}


def get_token() -> Sequence[Token]:
    return tokens[settings.CHAIN_ID]


def get_token_by_address(address: str) -> Token:
    tokens = get_token()

    for token in tokens:
        if token.address.lower() == address.lower():
            return token
