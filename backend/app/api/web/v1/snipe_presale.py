from fastapi import APIRouter, Request
from app.lib.response_schema import response_base
from app.lib.response_code import CustomResponseCode
from app.lib import errors
from starlette import status
from starlette.authentication import requires
from app.services.snipe_service import SnipeService
from app.common.logger import logger
from app.schemas.snipe import CreatePresale, Claim, SnipeToken

router = APIRouter()

@router.post("/create")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def create_presale(request: Request, param: CreatePresale):
  try:
    await SnipeService.create_presale(request=request, param=param)
    return await response_base.success()
  except errors.RequestError as exc:
    logger.error(exc)
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    logger.error(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail=e)


@router.post("/claim")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def claim(request: Request, param: Claim):
  try:
    SnipeService.claim(request=request, param=param)
    return await response_base.success()
  except errors.RequestError as exc:
    logger.error(exc)
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    logger.error(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail=e)


@router.post("/withdraw-contribution")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def withdrawContribution(request: Request, param: Claim):
  try:
    SnipeService.withdrawContribution(request=request, param=param)
    return await response_base.success()
  except errors.RequestError as exc:
    logger.error(exc)
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    logger.error(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail=e)
  

@router.post("/snipe-token")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def snipe_token(request: Request, param: SnipeToken):
  try:
    await SnipeService.snipe_token(request=request, param=param)
    return await response_base.success()
  except errors.RequestError as exc:
    logger.error(exc)
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    logger.error(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail=e)
  
  
@router.get("/")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def get(request: Request):
  try:
    presales = SnipeService.get(request=request)
    return await response_base.success(data=presales)
  except errors.RequestError as exc:
    logger.error(exc)
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    logger.error(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail=e)
  
  
@router.get("/{status}")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def get(request: Request, status: str):
  try:
    presales = SnipeService.get_by_status(request=request, status=status)
    return await response_base.success(data=presales)
  except errors.RequestError as exc:
    logger.error(exc)
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    logger.error(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail=e)
  