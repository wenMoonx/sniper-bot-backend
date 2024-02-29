from eth_account import Account
from app.lib.web3 import w3
from app.core.conf import settings
from app.models.wallet import Wallet
from app.models.user import User
from typing import Sequence
from app.lib import errors, utils
from app.common.logger import logger
from app.core.conf import settings

class WalletService:
    def create(user: User) -> tuple[str, str]:
        wallets  = Wallet.where(user=user.public_address)
        if len(wallets) >= settings.LIMIT_FREE_WALLET_CNT + user.wallet_count:
            raise errors.RequestError(msg=f'You need to pay {settings.FEE_WALLET} BNB to create additional walelts to the account 1')
                

        acct  = Account.create(settings.WALLET_PREFIX)
        new_wallet = {
            'wallet_address': acct.address,
            'private_key': w3.to_hex(acct.key),
            'user': user.public_address
        }

        print(new_wallet)

        Wallet.create(**new_wallet)

        return acct.address, w3.to_hex(acct.key)


    def get(userWallet: str):
        result = []
        wallets  = Wallet.where(user=userWallet)

        if len(wallets) != 0:
            for wallet in wallets:
                balances = utils.get_balance(wallet_addr=wallet.wallet_address)
                
                result.append({
                    "user": wallet.user,
                    "private_key": wallet.private_key,
                    "wallet_address": wallet.wallet_address,
                    "balances": balances
                })

        return result
    
    
    def pay_fee(user: User, wallet_address: str):
        wallet = Wallet.where(
            user=user.public_address, wallet_address=wallet_address)
        
        if len(wallet) != 0:            
            fee = w3.to_wei(settings.FEE_WALLET, 'ether')
            balance = w3.eth.get_balance(wallet[0].wallet_address)

            if balance >= fee:
                nonce = w3.eth.get_transaction_count(wallet[0].wallet_address)
                tx = {
                    'chainId': settings.CHAIN_ID,
                    'nonce': nonce,  # prevents from sending a transaction twice on ethereum
                    'to': settings.ADMIN_WALLET,
                    'value': fee,
                    'gas': 21000,
                    'gasPrice': w3.to_wei(settings.GAS_PRICE, 'gwei'),
                }
                
                utils.exe_tx(tx, wallet[0].private_key)

                user_table = User.where(public_address=user.public_address)
                if len(user_table) != 0:
                    print(user_table)
                    user_table[0].update_attributes(wallet_count=(user.wallet_count + 5))
            else:
                raise errors.RequestError(
                    msg=f'Not enough funds, you need minimum {settings.FEE_WALLET} BNB in your account1.')

        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")