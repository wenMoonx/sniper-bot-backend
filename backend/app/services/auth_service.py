from fastapi import Request
from datetime import datetime

from app.common import jwt
from app.lib import errors
from app.common.redis import redis_client
from app.core.conf import settings
from app.models.user import User
from app.schemas.user import LoginUser
import random
from app.lib.web3 import w3
from app.common.logger import logger
from eth_account import Account, messages


class AuthService:

    async def login(
        self, *, request: Request, param: LoginUser
    ) -> tuple[str, str, datetime, datetime, User]:
        try:
            current_user: User = User.find_by(public_address=param.publicAddress)
            if not current_user:
                new_user = {
                    'nonce': random.randint(0, 9999),
                    'public_address': param.publicAddress
                }
                current_user = User.create(**new_user)
            else:
                nonce = f'Sign this message to prove you have access to this wallet. Timestamp: {param.nonce}'
                # message = messages.encode_defunct(text=nonce)
                # sig = Account.sign_message(message, private_key='95ada91ccae7a16c11c25f1a3a2dcb8d6012c02983f5405a5392e90d93b5af42')
                # print("signature =", sig.signature.hex())
                message_hash = messages.encode_defunct(text=nonce)
                address = Account.recover_message(message_hash, signature=param.signature)

                if address.lower() != param.publicAddress.lower():
                    raise errors.NotFoundError(msg="Please check your signature")
            access_token, access_token_expire_time = await jwt.create_access_token(str(current_user.id))
            refresh_token, refresh_token_expire_time = await jwt.create_refresh_token(
                str(current_user.id), access_token_expire_time
            )
        except errors.NotFoundError as e:
            logger.info(e)
            raise errors.NotFoundError(msg=e.msg)
        except (errors.AuthorizationError, errors.CustomError) as e:
            logger.info(e)
            raise errors.AuthorizationError(msg=e.msg)
        except Exception as e:
            logger.info(e)
            raise errors.ServerError()
        else:
            return access_token, refresh_token, access_token_expire_time, refresh_token_expire_time, current_user


    @staticmethod
    async def logout(*, request: Request) -> None:
        token = await jwt.get_token(request)
        key = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:{token}'
        await redis_client.delete(key)
