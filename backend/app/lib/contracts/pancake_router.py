
from app.lib.web3 import w3
from web3 import Web3
from app.core.path_conf import BasePath
from app.core.conf import settings
import json


def use_swap_router():
  with open(f'{BasePath}/lib/contracts/pancake_router.json', 'rb') as file:
    abi = json.load(file)
    formated_address = Web3.to_checksum_address(settings.SWAP_ROUTER)    
    contract = w3.eth.contract(address=formated_address, abi=abi)
    return contract