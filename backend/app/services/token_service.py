from fastapi import Request
from app.models.wallet import Wallet
from app.schemas.token import TokenTransfer, MultiTokenTransfer, Swap, MultiTransferEth, MultiSwap
from app.lib.contracts.erc20_token import use_token
from app.lib.contracts.pancake_router import use_swap_router
from app.lib.token import get_token_by_address
from app.lib.web3 import w3, zero_address, Web3, get_tx_fee
from app.lib.token import wbnb
from app.lib.utils import exe_tx
from app.core.conf import settings
from app.lib import errors
import time
import asyncio


class TokenService:
    def get_rate(index: int):
        if index == 0:
            return 0.25
        elif index == 1:
            return 0.5
        elif index == 2:
            return 0.75
        else:
            return 

    def transfer(request: Request, param: TokenTransfer):
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=param.wallet)
        if len(wallet) != 0:
            balance = w3.eth.get_balance(param.wallet)
            if balance < w3.to_wei(settings.TX_FEE, 'ether'):
                raise errors.RequestError(
                    msg="Please check your BNB balance is enough to make the tx")

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
            exe_tx(transaction, wallet[0].private_key)

            nonce = w3.eth.get_transaction_count(param.wallet)
            transaction = contract.functions.transfer(param.receiver, amount).build_transaction({
                'from': param.wallet,
                'nonce': nonce,
            })
            exe_tx(transaction, wallet[0].private_key)

        else:
            raise errors.RequestError(
                msg="Please check the sender wallet is correct")
    

    def multi_transfer(request: Request, param: MultiTokenTransfer):
        for wallet_addr in param.wallets:

            wallet = Wallet.where(
                user=request.user.public_address, wallet_address=wallet_addr)
            if len(wallet) != 0:
                balance = w3.eth.get_balance(wallet_addr)
                if balance < w3.to_wei(settings.TX_FEE, 'ether'):
                    raise errors.RequestError(
                        msg="Please check your BNB balance is enough to make the tx")

                contract = use_token(param.token)
                token = get_token_by_address(param.token)            

                if token is None:
                    raise errors.RequestError(
                        msg='Send token is not allowed')
                
                balance = contract.functions.balanceOf(
                    wallet_addr).call()
                
                if balance == 0:
                    continue
                
                amount = int(balance * TokenService.get_rate(param.amount_type))

                nonce = w3.eth.get_transaction_count(wallet_addr)
                transaction = contract.functions.approve(Web3.to_checksum_address(settings.SWAP_ROUTER), amount).build_transaction({
                    'from': wallet_addr,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)

                nonce = w3.eth.get_transaction_count(wallet_addr)
                transaction = contract.functions.transfer(param.receiver, amount).build_transaction({
                    'from': wallet_addr,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)

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
                'to': Web3.to_checksum_address(param.receiver),
                'value': w3.to_wei(float(param.amount), 'ether'),
                'gas': 21000,
                'gasPrice': w3.to_wei(settings.GAS_PRICE, 'gwei'),
            }
            exe_tx(tx, wallet[0].private_key)
        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")


    async def transfer_eth_process(request: Request, param: MultiTransferEth, wallet_addr: str):
            balance = w3.eth.get_balance(wallet_addr)
            print(balance)
            if balance == 0:
                return None

            print('multi_transfer_eth')
            wallet = Wallet.where(
                user=request.user.public_address, wallet_address=wallet_addr)

            if len(wallet) != 0:
                nonce = w3.eth.get_transaction_count(wallet_addr)
                amount = int(balance * TokenService.get_rate(param.amount_type))
                
                receiver = Web3.to_checksum_address(param.receiver)

                tx_fee = get_tx_fee({
                    'from': wallet_addr,
                    'to': receiver,
                    'value': amount
                })

                if amount <= tx_fee:
                    return None

                tx = {
                    'chainId': settings.CHAIN_ID,
                    'nonce': nonce,  # prevents from sending a transaction twice on ethereum
                    'to': receiver,
                    'value': amount - tx_fee,
                    'gas': 21000,
                    'gasPrice': w3.to_wei(settings.GAS_PRICE, 'gwei'),
                }
                
                exe_tx(tx, wallet[0].private_key)
            else:
                raise errors.RequestError(
                    msg="Please check the wallet address is correct")


    async def multi_transfer_eth(request: Request, param: MultiTransferEth):
        await asyncio.gather(
            *(TokenService.transfer_eth_process(request, param, wallet_addr) for wallet_addr in param.wallets),
            return_exceptions = False
        )


    def swap(request: Request, param: Swap):
        print(param)
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=param.wallet)
        router_contract = use_swap_router()
        if len(wallet) != 0:
            if param.src_token == zero_address:
                amount = w3.to_wei(float(param.amount), 'ether')
                fee = int(amount * settings.ADMIN_FEE)
                amount = int(amount - fee)

                nonce = w3.eth.get_transaction_count(param.wallet)
                print(w3.to_wei(param.gas_price, 'gwei'))
                transaction = router_contract.functions.swapExactETHForTokens(
                    10,
                    [Web3.to_checksum_address(wbnb[settings.CHAIN_ID].address), Web3.to_checksum_address(
                        param.dst_token)],
                    param.wallet,
                    int(time.time() + settings.TX_REVERT_TIME)
                ).build_transaction({
                    'from': param.wallet,
                    'gasPrice': w3.to_wei(param.gas_price, 'gwei'),
                    'value': amount,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)
                
                nonce = w3.eth.get_transaction_count(param.wallet)
                tx = {
                    'chainId': settings.CHAIN_ID,
                    'nonce': nonce,  # prevents from sending a transaction twice on ethereum
                    'to': Web3.to_checksum_address(settings.ADMIN_WALLET),
                    'value': fee,
                    'gas': 21000,
                    'gasPrice': w3.to_wei(param.gas_price, 'gwei'),
                }
                exe_tx(tx, wallet[0].private_key)

            if param.dst_token == zero_address:
                token_contract = use_token(param.src_token)
                token = get_token_by_address(param.src_token)

                if token is None:
                    raise errors.RequestError(
                        msg='Swap token is not allowed')

                amount = int(param.amount * 10 ** token.decimals)
                fee = int(amount * settings.ADMIN_FEE)
                current_balance = token_contract.functions.balanceOf(
                    param.wallet).call()
                if amount > current_balance:
                    raise errors.RequestError(
                        msg="Please check your swap amount")

                amount = int(amount - fee)

                transaction = token_contract.functions.approve(Web3.to_checksum_address(settings.SWAP_ROUTER), amount).build_transaction({
                    'from': param.wallet,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)

                nonce = w3.eth.get_transaction_count(param.wallet)
                transaction = router_contract.functions.swapExactTokensForETH(
                    amount,
                    10,
                    [Web3.to_checksum_address(param.src_token), Web3.to_checksum_address(
                        wbnb[settings.CHAIN_ID].address)],
                    param.wallet,
                    int(time.time() + settings.TX_REVERT_TIME)
                ).build_transaction({
                    'from': param.wallet,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)

                nonce = w3.eth.get_transaction_count(param.wallet)
                transaction = token_contract.functions.transfer(Web3.to_checksum_address(settings.ADMIN_WALLET), fee).build_transaction({
                    'from': param.wallet,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)
        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")


    def swap_process(request: Request, param: MultiSwap, wallet_addr: str
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=wallet_addr)
        nonce = w3.eth.get_transaction_count(wallet_addr)
        router_contract = use_swap_router()
        if len(wallet) != 0:
            if param.src_token == zero_address:
                balance = w3.eth.get_balance(wallet_addr)
                print(f'balance: {balance}')
                if balance == 0:
                    continue

                amount = int(balance * TokenService.get_rate(param.amount_type))
                fee = int(amount * settings.ADMIN_FEE)

                tx_fee = get_tx_fee({
                    'from': Web3.to_checksum_address(wallet_addr),
                    'value': amount
                })

                print(fee)
                print(tx_fee)
                print(amount)
                
                if amount > tx_fee + fee:
                    amount = int(amount - fee - tx_fee)

                    transaction = router_contract.functions.swapExactETHForTokens(
                        10,
                        [Web3.to_checksum_address(wbnb[settings.CHAIN_ID].address), Web3.to_checksum_address(
                            param.dst_token)],
                        wallet_addr,
                        int(time.time() + settings.TX_REVERT_TIME)
                    ).build_transaction({
                        'from': wallet_addr,
                        'gasPrice': w3.to_wei(param.gas_price, 'gwei'),
                        # This is the Token(BNB) amount you want to Swap from
                        'value': amount,
                        'nonce': nonce,
                    })
                    exe_tx(transaction, wallet[0].private_key)
                    
                    nonce = w3.eth.get_transaction_count(wallet_addr)
                    tx = {
                        'chainId': settings.CHAIN_ID,
                        'nonce': nonce,  # prevents from sending a transaction twice on ethereum
                        'to': Web3.to_checksum_address(settings.ADMIN_WALLET),
                        'value': fee,
                        'gas': 21000,
                        'gasPrice': w3.to_wei(param.gas_price, 'gwei'),
                    }
                    exe_tx(tx, wallet[0].private_key)
                
                else:
                    continue

            if param.dst_token == zero_address:
                token_contract = use_token(param.src_token)
                token = get_token_by_address(param.src_token)

                if token is None:
                    raise errors.RequestError(
                        msg='Swap token is not allowed')

            
                balance = token_contract.functions.balanceOf(
                    wallet_addr).call()
                
                if balance == 0:
                    continue
                
                amount = int(balance * TokenService.get_rate(param.amount_type))
                fee = int(amount * settings.ADMIN_FEE)
                amount = int(amount - fee)

                transaction = token_contract.functions.approve(Web3.to_checksum_address(settings.SWAP_ROUTER), amount).build_transaction({
                    'from': wallet_addr,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)

                nonce = w3.eth.get_transaction_count(wallet_addr)
                transaction = router_contract.functions.swapExactTokensForETH(
                    amount,
                    10,
                    [Web3.to_checksum_address(param.src_token), Web3.to_checksum_address(
                        wbnb[settings.CHAIN_ID].address)],
                    wallet_addr,
                    int(time.time() + settings.TX_REVERT_TIME)
                ).build_transaction({
                    'from': wallet_addr,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)
                
                nonce = w3.eth.get_transaction_count(wallet_addr)
                transaction = token_contract.functions.transfer(Web3.to_checksum_address(settings.ADMIN_WALLET), fee).build_transaction({
                    'from': wallet_addr,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet[0].private_key)

        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")
    
    async def multi_swap(request: Request, param: MultiSwap):
        print(param)
        
        await asyncio.gather(
            *(TokenService.swap_process(request, param, wallet_addr) for wallet_addr in param.wallets),
            return_exceptions = False
        )