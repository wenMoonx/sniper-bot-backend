from asgiref.sync import sync_to_async
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from datetime import datetime, timedelta
from jose import jwt
from app.lib import errors
from passlib.context import CryptContext
from app.lib.timezone import timezone
from app.common.redis import redis_client
from app.core.conf import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def create_access_token(sub: str, **kwargs) -> tuple[str, datetime]:
    """
    Generate encryption token

    :param sub: The subject/userid of the JWT
    :param expires_delta: Increased expiry time
    :return:
    """

    expire = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
    expire_seconds = settings.TOKEN_EXPIRE_SECONDS
    to_encode = {'exp': expire, 'sub': sub, **kwargs}
    token = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)

    key = f'{settings.TOKEN_REDIS_PREFIX}:{sub}:{token}'
    await redis_client.setex(key, expire_seconds, token)
    return token, expire


async def create_refresh_token(sub: str, expire_time: datetime | None = None, **kwargs) -> tuple[str, datetime]:
    """
    Generate encryption refresh token, only used to create a new token

    :param sub: The subject/userid of the JWT
    :param expire_time: expiry time
    :return:
    """
    if expire_time:
        expire = expire_time + timedelta(seconds=settings.TOKEN_REFRESH_EXPIRE_SECONDS)
        expire_datetime = timezone.f_datetime(expire_time)
        current_datetime = timezone.now()
        if expire_datetime < current_datetime:
            raise errors.TokenError(msg='Refresh Token Expiration time is invalid')
        expire_seconds = int((expire_datetime - current_datetime).total_seconds())
    else:
        expire = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
        expire_seconds = settings.TOKEN_REFRESH_EXPIRE_SECONDS
    to_encode = {'exp': expire, 'sub': sub, **kwargs}
    refresh_token = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)

    key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:{refresh_token}'
    await redis_client.setex(key, expire_seconds, refresh_token)
    
    return refresh_token, expire

@sync_to_async
def get_token(request: Request) -> str:
    """
    Get token for request header

    :return:
    """
    authorization = request.headers.get('Authorization')
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != 'bearer':
        raise errors.TokenError(msg='Token invalid')
    return token

async def jwt_decode(token: str) -> str:
    """
    Decode token

    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        user_id = payload.get('sub')
        if not user_id:
            raise errors.TokenError(msg='Token invalid')
    except jwt.ExpiredSignatureError:
        raise errors.TokenError(msg='Token expired')
    except (jwt.JWTError, Exception) as e:
        raise errors.TokenError(msg='Token invalid')
    return user_id


@sync_to_async
def password_verify(plain_password: str, hashed_password: str) -> bool:
    """
    Password verification

    :param plain_password: The password to verify
    :param hashed_password: The hash ciphers to compare
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)

async def jwt_authentication(token: str) -> str:
    """
    JWT authentication

    :param token:
    :return:
    """
    user_id = await jwt_decode(token)
    key = f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{token}'

    token_verify = await redis_client.get(key)
    if not token_verify:
        raise errors.TokenError(msg='Token expired')

    return user_id    

@sync_to_async
def get_hash_password(password: str) -> str:
    """
    Encrypt passwords using the hash algorithm

    :param password:
    :return:
    """
    return pwd_context.hash(password)
                              