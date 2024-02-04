
from fastapi import APIRouter, Request
from app.schemas.user import LoginUser
from app.services.auth_service import AuthService
from app.lib.response_schema import response_base, CustomResponseCode
from app.lib import errors
from starlette.authentication import requires
from starlette import status


router = APIRouter()

@router.post("/login", 
    summary='User login',
)
async def login(param: LoginUser, request: Request):
	try:
		print(param)
		access_token, refresh_token, access_expire, refresh_expire, user = await AuthService().login(
        request=request, param=param
    )
		data = {
			'access_token': access_token,
			'refresh_token': refresh_token,
			'access_expire': access_expire,
			'refresh_expire': refresh_expire,
			'user': user
		}

		return await response_base.success(data=data)
	
	except errors.NotFoundError as exc:
		print(exc)
		return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_404)
	except errors.AuthorizationError as exc:
		print(exc)
		return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_401)
	except Exception as e:
		print(e)
		return await response_base.fail(error_detail=getattr(e, 'msg', 'Internal server error'))


@router.post('/logout', summary='User logout')
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def logout(request: Request):
	try:
		await AuthService.logout(request=request)
		return await response_base.success()
	except Exception as e:
		return await response_base.fail()
