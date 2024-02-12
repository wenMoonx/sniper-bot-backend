from web3 import Web3
from app.core.conf import settings
from web3.middleware import geth_poa_middleware

w3 = Web3(Web3.HTTPProvider(settings.RPC_SERVER_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

zero_address = "0x0000000000000000000000000000000000000000"

