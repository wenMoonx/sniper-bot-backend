
from app.lib.web3 import w3
from web3 import Web3
from app.core.path_conf import BasePath
import json


def use_token(token: str):
  with open(f'{BasePath}/lib/contracts/erc20_abi.json', 'rb') as file:
    abi = json.load(file)
    formated_address = Web3.to_checksum_address(token)    
    contract = w3.eth.contract(address=formated_address, abi=abi)
    return contract