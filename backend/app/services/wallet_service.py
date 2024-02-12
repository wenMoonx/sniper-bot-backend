from eth_account import Account
from app.lib.web3 import w3
from app.core.conf import settings
from app.models.wallet import Wallet
from app.models.user import User
from typing import Sequence
from app.lib import errors
from app.common.logger import logger

class WalletService:
    def create(user: User) -> tuple[str, str]:
        wallets  = Wallet.where(user=user.public_address)
        if len(wallets) > settings.LIMIT_FREE_WALLET_CNT + user.wallet_count:
            raise errors.RequestError(msg="You need to pay bnb token to create additional walelts")
                

        acct  = Account.create(settings.WALLET_PREFIX)
        new_wallet = {
            'wallet_address': acct.address,
            'private_key': w3.to_hex(acct.key),
            'user': user.public_address
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
    
    
    def pay_fee(user: User, wallet_address: str):
        wallet = Wallet.where(
            user=user.public_address, wallet_address=wallet_address)
        
        if len(wallet) != 0:            
            fee = w3.to_wei(1, 'ether')
            balance = w3.eth.get_balance(wallet[0].wallet_address)

            if balance >= fee:
                nonce = w3.eth.get_transaction_count(wallet[0].wallet_address)
                tx = {
                    'chainId': settings.CHAIN_ID,
                    'nonce': nonce,  # prevents from sending a transaction twice on ethereum
                    'to': settings.ADMIN_WALLET,
                    'value': w3.to_wei(1, 'ether'),
                    'gas': 2000000,
                    'gasPrice': w3.to_wei('50', 'gwei'),
                }

                signed_tx = w3.eth.account.sign_transaction(
                    tx, wallet[0].private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                w3.eth.wait_for_transaction_receipt(tx_hash)

                User.update_attributes({
                    'wallet_count': user.wallet_count + 5,
                }).where({
                    'public_address': user.public_address,
                })
            else:
                raise errors.RequestError(
                    msg="You need to check the balance of wallet is bigger than fee")

        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")
