from fastapi import APIRouter, Request
from app.lib.response_schema import response_base
from app.lib.response_code import CustomResponseCode
from app.lib import errors
from starlette import status
from starlette.authentication import requires
from app.services.wallet_service import WalletService
from app.schemas.wallet import PayFee
from app.common.logger import logger

router = APIRouter()

@router.post("/")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def create(request: Request):
  try:
    wallet_address, private_key = WalletService.create(user=request.user)
    wallet = {
      'wallet_address': wallet_address,
      'private_key': private_key
    }
    return await response_base.success(data=wallet)
  except errors.RequestError as exc:
    logger.info(exc)
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    logger.info(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail="")

@router.post("/pay-fee")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def pay_fee(request: Request, param: PayFee):
  try:
    WalletService.pay_fee(user=request.user, wallet_address=param.wallet_address)
    return await response_base.success()
  except errors.RequestError as exc:
    logger.info(exc)
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    logger.info(e)
    return await response_base.fail(res=CustomResponseCode.HTTP_500, error_detail="")
  

@router.get("/")
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
async def index(request: Request):
  try:
    wallets = WalletService.get(userWallet=request.user.public_address)
    return await response_base.success(data=wallets)
  except errors.RequestError as exc:
    return await response_base.fail(error_detail=exc.msg, res=CustomResponseCode.HTTP_400)
  except Exception as e:
    return await response_base.fail(res=CustomResponseCode.HTTP_500)