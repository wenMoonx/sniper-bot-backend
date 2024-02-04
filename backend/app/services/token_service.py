from fastapi import Request
from app.models.wallet import Wallet
from app.schemas.token import TokenTransfer, Swap
from app.lib.contracts.erc20_token import use_token
from app.lib.contracts.pancake_router import use_swap_router
from app.lib.token import get_token_by_address
from app.lib.web3 import w3
from app.core.conf import settings
from app.lib import errors
from app.lib.timezone import timezone


class TokenService:
  def transfer(request: Request, param: TokenTransfer):
    wallet = Wallet.where(user = request.user.public_address, wallet_address=param.wallet)
    if len(wallet) != 0:    
      contract = use_token(param.token)
      nonce = w3.eth.get_transaction_count(param.wallet)
      transaction = contract.functions.transfer(param.receiver, param.amount).build_transaction({
        'from': param.wallet,  
        'nonce': nonce,
      })
      signed_txn = w3.eth.account.sign_transaction(transaction, wallet[0].private_key)
      tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
      w3.eth.wait_for_transaction_receipt(tx_hash)

    else:
      raise errors.RequestError(msg="Please check the sender wallet is correct")

  def transfer_eth(request: Request, param: TokenTransfer):
    try:
      wallet = Wallet.where(user=request.user.public_address, wallet_address=param.wallet)
      
      if len(wallet) != 0:    
        nonce = w3.eth.get_transaction_count(param.wallet)
        tx = {
          'nonce': nonce,  #prevents from sending a transaction twice on ethereum
          'to': param.receiver,
          'value': param.amount,
          'gas': 2000000,
          'gasPrice': w3.to_wei(50, 'gwei')
        }
        
        signed_tx = w3.eth.account.sign_transaction(tx, wallet[0].private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
      else:
        raise errors.RequestError(msg="Please check the wallet address is correct")
    except Exception as e:
      print(e)
      raise errors.ServerError()
  
  def swap(request: Request, param: Swap):
    try:
      wallet = Wallet.where(user=request.user.public_address, wallet_address=param.wallet)
      
      if len(wallet) != 0:
        token_contract = use_token(param.src_token)
        nonce = w3.eth.get_transaction_count(param.wallet)
        token = get_token_by_address(param.src_token)
        transaction = token_contract.functions.approve(settings.SWAP_ROUTER, param.amount * 10 ** token.decimals).build_transaction({
          'from': param.wallet,  
          'nonce': nonce,
        })
        signed_txn = w3.eth.account.sign_transaction(transaction, wallet[0].private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

        router_contract = use_swap_router()
        nonce = w3.eth.get_transaction_count(param.wallet)
        transaction = router_contract.functions.swapExactTokensForTokens(
          param.amount * 10 ** token.decimals,
          0,
          [param.src_token, param.dst_token],
          wallet[0].address,
          int(timezone.now() + 3600 * 24)
        ).build_transaction({
          'from': param.wallet,  
          'nonce': nonce,
        })
        signed_txn = w3.eth.account.sign_transaction(transaction, wallet[0].private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
      else:
        raise errors.RequestError(msg="Please check the wallet address is correct")
    except Exception as e:
      print(e)
      raise errors.ServerError()