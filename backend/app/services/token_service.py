from fastapi import Request
from app.models.wallet import Wallet
from app.schemas.token import TokenTransfer, Swap
from app.lib.contracts.erc20_token import use_token
from app.lib.contracts.pancake_router import use_swap_router
from app.lib.token import get_token_by_address
from app.lib.web3 import w3, zero_address, Web3
from app.core.conf import settings
from app.lib import errors
import time


class TokenService:
    def transfer(request: Request, param: TokenTransfer):
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=param.wallet)
        if len(wallet) != 0:
            contract = use_token(param.token)
            token = get_token_by_address(param.token)            

            if token is None:
                raise errors.RequestError(
                    msg='Send token is not allowed')
            
            amount = int(param.amount * 10 ** token.decimals)
            current_balance = contract.functions.balanceOf(
                param.wallet).call()
            if amount > current_balance:
                raise errors.RequestError(
                    msg="Please check your transfer amount")

            nonce = w3.eth.get_transaction_count(param.wallet)
            transaction = contract.functions.approve(Web3.to_checksum_address(settings.SWAP_ROUTER), amount).build_transaction({
                'from': param.wallet,
                'nonce': nonce,
            })
            signed_txn = w3.eth.account.sign_transaction(
                transaction, wallet[0].private_key)
            tx_hash = w3.eth.send_raw_transaction(
                signed_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)
            nonce = w3.eth.get_transaction_count(param.wallet)

            transaction = contract.functions.transfer(param.receiver, amount).build_transaction({
                'from': param.wallet,
                'nonce': nonce,
            })
            signed_txn = w3.eth.account.sign_transaction(
                transaction, wallet[0].private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)

        else:
            raise errors.RequestError(
                msg="Please check the sender wallet is correct")

    def transfer_eth(request: Request, param: TokenTransfer):
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=param.wallet)

        if len(wallet) != 0:
            nonce = w3.eth.get_transaction_count(param.wallet)
            tx = {
                'chainId': settings.CHAIN_ID,
                'nonce': nonce,  # prevents from sending a transaction twice on ethereum
                'to': param.receiver,
                'value': w3.to_wei(float(param.amount), 'ether'),
                'gas': 2000000,
                'gasPrice': w3.to_wei('50', 'gwei'),
            }

            signed_tx = w3.eth.account.sign_transaction(
                tx, wallet[0].private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)
        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")

    def swap(request: Request, param: Swap):
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=param.wallet)
        nonce = w3.eth.get_transaction_count(param.wallet)
        router_contract = use_swap_router()
        if len(wallet) != 0:
            if param.src_token == zero_address:
                transaction = router_contract.functions.swapExactETHForTokens(
                    10,
                    [Web3.to_checksum_address('0xEC5dCb5Dbf4B114C9d0F65BcCAb49EC54F6A0867'), Web3.to_checksum_address(
                        param.dst_token)],
                    param.wallet,
                    int(time.time() + settings.TX_REVERT_TIME)
                ).build_transaction({
                    'from': param.wallet,
                    'gasPrice': w3.to_wei('10', 'gwei'),
                    # This is the Token(BNB) amount you want to Swap from
                    'value': w3.to_wei(float(param.amount), 'ether'),
                    'nonce': nonce,
                })

                signed_txn = w3.eth.account.sign_transaction(
                    transaction, wallet[0].private_key)
                tx_hash = w3.eth.send_raw_transaction(
                    signed_txn.rawTransaction)
                w3.eth.wait_for_transaction_receipt(tx_hash)

                print(tx_hash)

            if param.dst_token == zero_address:
                token_contract = use_token(param.src_token)
                token = get_token_by_address(param.src_token)

                if token is None:
                    raise errors.RequestError(
                        msg='Swap token is not allowed')

                amount = int(param.amount * 10 ** token.decimals)
                current_balance = token_contract.functions.balanceOf(
                    param.wallet).call()
                if amount > current_balance:
                    raise errors.RequestError(
                        msg="Please check your swap amount")

                transaction = token_contract.functions.approve(Web3.to_checksum_address(settings.SWAP_ROUTER), amount).build_transaction({
                    'from': param.wallet,
                    'nonce': nonce,
                })
                signed_txn = w3.eth.account.sign_transaction(
                    transaction, wallet[0].private_key)
                tx_hash = w3.eth.send_raw_transaction(
                    signed_txn.rawTransaction)
                w3.eth.wait_for_transaction_receipt(tx_hash)

                nonce = w3.eth.get_transaction_count(param.wallet)
                transaction = router_contract.functions.swapExactTokensForETH(
                    amount,
                    10,
                    # 0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd
                    [Web3.to_checksum_address(param.src_token), Web3.to_checksum_address(
                        '0xEC5dCb5Dbf4B114C9d0F65BcCAb49EC54F6A0867')],
                    param.wallet,
                    int(time.time() + settings.TX_REVERT_TIME)
                ).build_transaction({
                    'from': param.wallet,
                    'nonce': nonce,
                })

                signed_txn = w3.eth.account.sign_transaction(
                    transaction, wallet[0].private_key)
                tx_hash = w3.eth.send_raw_transaction(
                    signed_txn.rawTransaction)
                w3.eth.wait_for_transaction_receipt(tx_hash)

                print(tx_hash)
        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")
