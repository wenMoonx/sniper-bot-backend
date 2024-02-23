from functools import lru_cache
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    # Env Postgres
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Administrator
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # Env Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DATABASE: int

    # FastAPI
    API_V1_STR: str = '/web/api/v1'
    TITLE: str = 'Sniper Bot'
    VERSION: str = '0.0.1'
    DESCRIPTION: str = 'Sniper Bot'
    DOCS_URL: str | None = f'{API_V1_STR}/docs'

    # Uvicorn
    UVICORN_HOST: str = '127.0.0.1'
    UVICORN_PORT: int = 8000
    UVICORN_RELOAD: bool = True

    # Limiter
    LIMITER_REDIS_PREFIX: str = 'corpy_limiter'

    # DateTime
    DATETIME_TIMEZONE: str = 'Asia/Tokyo'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Redis
    REDIS_TIMEOUT: int = 5

    # WEB3
    # RPC_SERVER_URL: str = 'https://bsc-testnet.publicnode.com'
    RPC_SERVER_URL: str = 'https://bsc-dataseed1.ninicoin.io'
    # CHAIN_ID: int = 97
    CHAIN_ID: int = 56
    WALLET_PREFIX: str = 'KEYSMASH FJAFJKLDSKF7JKFDJ 1530'
    LIMIT_FREE_WALLET_CNT: int = 5
    SWAP_ROUTER: str
    ADMIN_WALLET: str
    TX_REVERT_TIME: int = 3600 * 2
    FEE_WALLET: float = 0.001
    ADMIN_FEE: float = 0.01 # Percent
    TX_FEE: float = 0.0001
    GAS_PRICE: int = 3

    # Token
    TOKEN_ALGORITHM: str = 'HS256'  # algorithm
    TOKEN_SECRET_KEY: str = 'corpy_secret'
    TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1  # Expiration time, unit: seconds
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # Refresh expiration time, unit: seconds
    TOKEN_REDIS_PREFIX: str = 'corpy_token'
    TOKEN_REFRESH_REDIS_PREFIX: str = 'corpy_refresh_token'
    TOKEN_EXCLUDE: list[str] = [  # whitelist
        f'{API_V1_STR}/auth/login',
    ]
    TOKEN_API_KEY: str = 'W2MB66ZHH28HXMRUM6FZ5H2NJNWHNG4AHH'
    TOKEN_BALANCE_URL: str = f'https://api.bscscan.com/api?module=account&action=addresstokenbalance&apikey={TOKEN_API_KEY}'

    # Middleware
    MIDDLEWARE_CORS: bool = True

@lru_cache
def get_settings():
    """Read configuration optimization"""
    return Settings()


settings = get_settings()
