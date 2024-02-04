from eth_account import Account
from app.lib.web3 import w3
from app.core.conf import settings
from app.models.wallet import Wallet
from typing import Sequence
from app.lib import errors
from app.common.logger import logger
from app.core.conf import settings

class WalletService:
    def create(userWallet: str) -> tuple[str, str]:
        acct  = Account.create(settings.WALLET_PREFIX)
        wallets  = Wallet.where(user=userWallet)
        if len(wallets) > settings.LIMIT_FREE_WALLET_CNT:
            raise errors.RequestError(msg="You need to pay bnb token to create additional walelts")

        new_wallet = {
            'wallet_address': acct.address,
            'private_key': w3.to_hex(acct.key),
            'user': userWallet
        }

        Wallet.create(**new_wallet)

        return acct.address, w3.to_hex(acct.key)


    def get(userWallet: str) -> Sequence[Wallet]:
        try:
            wallets  = Wallet.where(user=userWallet)

            return wallets
        except Exception as e:
            logger.info(e)
            raise errors.ServerError()
    
