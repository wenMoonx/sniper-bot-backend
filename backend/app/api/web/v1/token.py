from fastapi import APIRouter, Request
from app.lib.response_schema import response_base
from app.lib.response_code import CustomResponseCode
from app.lib import errors
from starlette import status
from starlette.authentication import requires
from app.services.token_service import TokenService
from app.schemas.token import TokenTransfer, Swap
from app.lib.token import get_token

router = APIRouter()

@router.get("/token-list")
async def get(request: Request):
  try:
    tokens = get_token()
    return await response_base.success(data=tokens)
  except errors.RequestError as exc:
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    return await response_base.fail(res=CustomResponseCode.HTTP_500)

@router.post("/transfer")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def transfer(request: Request, param: TokenTransfer):
  try:
    TokenService.transfer(request=request, param=param)
    return await response_base.success()
  except errors.RequestError as exc:
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    print(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail="Please check transfer amount")


@router.post("/transfer-eth")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def transfer_eth(request: Request, param: TokenTransfer):
  try:
    TokenService.transfer_eth(request=request, param=param)
    return await response_base.success()
  except errors.RequestError as exc:
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    print(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500)
  

@router.post("/swap")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def swap(request: Request, param: Swap):
  try:
    TokenService.swap(request=request, param=param)
    return await response_base.success()
  except errors.RequestError as exc:
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    print(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500)