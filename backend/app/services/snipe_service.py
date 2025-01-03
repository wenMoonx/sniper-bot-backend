from fastapi import Request

from app.lib import errors
import threading
from app.core.conf import settings
from app.schemas.snipe import CreatePresale, Claim, SnipeToken
from app.lib.web3 import w3, Web3, zero_address
from app.lib.timezone import timezone
from app.common.logger import logger
from app.lib.timezone import timezone
from app.models.wallet import Wallet
from app.lib.contracts.presale import use_presale
from app.lib.contracts.pair_token import use_pair
from app.models.presale_snipe import PresaleSnipe
from app.lib.contracts.erc20_token import use_token
from app.lib.contracts.pancake_router import use_swap_router
from app.lib.utils import extract_wallet_address, exe_tx
import time
import asyncio

class SnipeService:
    def listen_finalize(contract_address: str, wallet: Wallet):
        logger.info('started listen_finalize')
        while True:
            presale_contract = use_presale(contract_address)
            event_filter = presale_contract.events.Finalized.create_filter(fromBlock='latest')
            
            for pair in event_filter.get_new_entries():
                logger.info('finalized')
                nonce = w3.eth.get_transaction_count(wallet.wallet_address)
                transaction = presale_contract.functions.claim().build_transaction({
                    'from': wallet.wallet_address,
                    'nonce': nonce,
                })
                exe_tx(transaction, wallet.private_key)
                
                presale_snipe_table = PresaleSnipe.where(wallet_address=wallet.wallet_address, presale_contract=contract_address)
                if len(presale_snipe_table) != 0:
                    presale_snipe_table[0].update_attributes(pair=pair, status='finalized')

                logger.info('finished finalized')

                break
    

    def listen_presale_start(contract_address: str, wallet: Wallet, amount: int, gas_price: float):
        logger.info('paased listen_presale_start')
        while True:
            presale_contract = use_presale(contract_address)
            start_date = presale_contract.functions.getTime().call()
            print(start_date)
            remain_time = timezone.f_get_diff(start_date)
            print(remain_time)
            if remain_time < 5:
                logger.info('started presale')
                nonce = w3.eth.get_transaction_count(wallet.wallet_address)
                transaction = presale_contract.functions.contribute(0, zero_address).build_transaction({
                    'from': wallet.wallet_address,
                    'nonce': nonce,
                    'to': contract_address,
                    'value': w3.to_wei(float(amount), 'ether'),
                    'chainId': settings.CHAIN_ID,     
                    'gas': 21000,
                    'gasPrice': w3.to_wei(gas_price, 'gwei'),
                })
                exe_tx(transaction, wallet.private_key)
                logger.info('contributed successfully')

                timeStampThread = threading.Thread(target=SnipeService.listen_finalize, args=(contract_address, wallet))
                timeStampThread.start()

                break

    def listen_add_liquidity(presale_snipe: PresaleSnipe, wallet: Wallet, amount: int):
        pair_contract = use_pair(presale_snipe.pair)
        router_contract = use_swap_router()
        token_contract = use_token(presale_snipe.token)
        # token = get_token_by_address(presale_snipe.token)
        
        decimals = token_contract.functions.decimals().call()
        amount = int(amount * 10 ** decimals)
        
        presale_snipe_table = PresaleSnipe.where(wallet_address=wallet.wallet_address, presale_contract=presale_snipe.presale_contract)
        if len(presale_snipe_table) != 0:
            presale_snipe_table[0].update_attributes(status='started')
        
        logger.info('started listen_add_liquidity')
        
        try:
            while True:
                event_filter = pair_contract.events.Mint.create_filter(fromBlock='latest')
                logger.info('started add_liquidity')
                for sender, amount0, amount1 in event_filter.get_new_entries():
                    nonce = w3.eth.get_transaction_count(wallet.wallet_address)
                    transaction = token_contract.functions.approve(Web3.to_checksum_address(settings.SWAP_ROUTER), amount).build_transaction({
                        'from': wallet.wallet_address,
                        'nonce': nonce,
                    })
                    exe_tx(transaction, wallet.private_key)

                    nonce = w3.eth.get_transaction_count(wallet.wallet_address)
                    transaction = router_contract.functions.swapExactTokensForTokens(
                        amount,
                        10,
                        [Web3.to_checksum_address(presale_snipe.token), Web3.to_checksum_address(
                            presale_snipe.currency)],
                        wallet.wallet_address,
                        int(time.time() + settings.TX_REVERT_TIME)
                    ).build_transaction({
                        'from': wallet.wallet_address,
                        'nonce': nonce,
                    })
                    exe_tx(transaction, wallet.private_key)
            
                    presale_snipe_table = PresaleSnipe.where(wallet_address=wallet.wallet_address, presale_contract=presale_snipe.presale_contract)
                    if len(presale_snipe_table) != 0:
                        presale_snipe_table[0].update_attributes(status='finished')

                    logger.info('finished add_liquidity')

                    break
        except Exception as e:
            logger.error(e)
            presale_snipe_table = PresaleSnipe.where(wallet_address=wallet.wallet_address, presale_contract=presale_snipe.presale_contract)
            if len(presale_snipe_table) != 0:
                presale_snipe_table[0].update_attributes(status='failed')
            

    def listen_contribute(contract_address: str, wallet: Wallet, token: str):
        while True:
            presale_contract = use_presale(contract_address)
            event_filter = presale_contract.events.Contributed.create_filter(fromBlock='latest')
            for sender, currency, amount, contributionAmount, time in event_filter.get_new_entries():
                new_presale = {
                    'wallet_address': wallet.wallet_address,
                    'currency': currency,
                    'presale_contract': contract_address,
                    'status': 'contributed',
                    'token': token
                }

                PresaleSnipe.create(**new_presale)
                break
                
    async def create_presale_process(request: Request, param: CreatePresale, wallet_addr: str):
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=wallet_addr)
        if len(wallet) != 0:
            presale_contract_addr = extract_wallet_address(param.url)
            print(presale_contract_addr)
            presale_contract = use_presale(presale_contract_addr)
            logger.info('checking min, max check')
            min, max = presale_contract.functions.getContributionSettings().call()
            amount = w3.to_wei(param.amount, 'ether')
            print(amount)
            print(min)
            print(max)
            poolSettings = presale_contract.functions.poolSettings().call()
            print(poolSettings)
            if amount >= min and amount <= max:
                logger.info('paased min, max check')
                timeStampThread = threading.Thread(target=SnipeService.listen_presale_start, args=(presale_contract_addr, wallet[0], param.amount, param.gas_price))
                timeStampThread.start()

                contributeThread = threading.Thread(target=SnipeService.listen_contribute, args=(presale_contract_addr, wallet[0], poolSettings[0]))
                contributeThread.start()
            else:
                raise errors.RequestError(
                    msg=f'Your contribution amount will be higher than {w3.from_wei(min, "ether")}')
        else:
            raise errors.RequestError(
                msg="Please check the sender wallet is correct")


    async def create_presale(
        request: Request,
        param: CreatePresale
    ):
        await asyncio.gather(
            *(SnipeService.create_presale_process(request, param, wallet_addr) for wallet_addr in param.wallets),
            return_exceptions = False
        )
        


    def claim(request: Request, param: Claim):
        presale_contract_addr = extract_wallet_address(param.url)
        presale_contract = use_presale(presale_contract_addr)
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=param.wallet)
        
        if len(wallet) != 0:
            nonce = w3.eth.get_transaction_count(wallet[0].wallet_address)
            transaction = presale_contract.functions.claim().build_transaction({
                'from': wallet[0].wallet_address,
                'nonce': nonce,
            })
            exe_tx(transaction, wallet[0].private_key)
            
        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")
        

    def withdrawContribution(request: Request, param: Claim):
        presale_contract_addr = extract_wallet_address(param.url)
        presale_contract = use_presale(presale_contract_addr)
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=param.wallet)
        
        if len(wallet) != 0:
            nonce = w3.eth.get_transaction_count(wallet[0].wallet_address)
            transaction = presale_contract.functions.emergencyWithdrawContribution().build_transaction({
                'from': wallet[0].wallet_address,
                'nonce': nonce,
            })
            exe_tx(transaction, wallet[0].private_key)
            
        else:
            raise errors.RequestError(
                msg="Please check the wallet address is correct")

  
    async def snipe_token_process(request: Request, param: SnipeToken, wallet_addr: str):
        presale_snipe = PresaleSnipe.where(
            presale_contract=param.contract, wallet_address=wallet_addr)
        
        wallet = Wallet.where(
            user=request.user.public_address, wallet_address=wallet_addr)
        
        if len(presale_snipe) != 0 and len(wallet) != 0:
            timeStampThread = threading.Thread(target=SnipeService.listen_add_liquidity, args=(presale_snipe[0], wallet[0], param.amount))
            timeStampThread.start()       
        else:
            raise errors.RequestError(
                msg="Please check your parameters are correct.")
                
  
    async def snipe_token(request: Request, param: SnipeToken):
        await asyncio.gather(
            *(SnipeService.snipe_token_process(request, param, wallet_addr) for wallet_addr in param.wallets),
            return_exceptions = False
        )
        
    
    def get(request: Request):
        
        result = []
        wallets  = Wallet.where(user=request.user.public_address)

        if len(wallets) != 0:
            for wallet in wallets:
                presale_snipe = PresaleSnipe.where(wallet_address=wallet.wallet_address)
                if len(presale_snipe) != 0:                   
                    result.append(presale_snipe[0])

        return result
        
    
    def get_by_status(request: Request, status: str):
        
        result = []
        wallets  = Wallet.where(user=request.user.public_address)

        if len(wallets) != 0:
            for wallet in wallets:
                presale_snipe = PresaleSnipe.where(wallet_address=wallet.wallet_address, status=status)

                if len(presale_snipe) != 0:                   
                    result.append(presale_snipe[0])

        return result