from web3 import Web3
from app.core.conf import settings
from web3.middleware import geth_poa_middleware
from app.schemas.token import Tx

w3 = Web3(Web3.HTTPProvider(settings.RPC_SERVER_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

zero_address = "0x0000000000000000000000000000000000000000"

def get_tx_fee(tx: Tx):
  gas_price = w3.eth.gas_price
  estimate_gas = w3.eth.estimate_gas(tx)
  print(gas_price * estimate_gas)
  return gas_price * estimate_gas
