from typing import Any

from fastapi import Request, Response
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from app.lib.errors import TokenError
from app.common.jwt import jwt_authentication
from app.models.user import User


class _AuthenticationError(AuthenticationError):
    """Override internal authentication error classes"""

    def __init__(self, *, code: int = None, msg: str = None, headers: dict[str, Any] | None = None):
        self.code = code
        self.msg = msg
        self.headers = headers


class JwtAuthMiddleware(AuthenticationBackend):
    """JWT Authentication middleware"""

    @staticmethod
    def auth_exception_handler(conn: HTTPConnection, exc: _AuthenticationError) -> Response:
        """Override internal authentication error handling"""
        return JSONResponse(content={'status': {'code': exc.code, 'message': exc.msg, 'error_detail': ''}, 'data': None}, status_code=exc.code)

    async def authenticate(self, request: Request):
        print(request)
        auth = request.headers.get('Authorization')
        if not auth:
            return
        scheme, token = auth.split()
        if scheme.lower() != 'bearer':
            return

        try:
            sub = await jwt_authentication(token)
            user: User = User.find(sub)
            if user is not None:
                return AuthCredentials(['authenticated']), user
            else:
                raise _AuthenticationError(code=getattr(e, 'code', HTTP_401_UNAUTHORIZED), msg=getattr(e, 'msg', 'Current user does not exist on current database '))
        except TokenError as exc:
            raise _AuthenticationError(code=exc.code, msg=exc.detail, headers=exc.headers)
        except Exception as e:
            print(e)
            raise _AuthenticationError(code=getattr(e, 'code', HTTP_401_UNAUTHORIZED), msg=getattr(e, 'msg', 'You need to signin again'))

        # Middleware, execution order from bottom to top
        # Please see the standard return mode：https://www.starlette.io/authentication/
