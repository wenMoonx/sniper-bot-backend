import re
from app.lib.web3 import w3

def extract_wallet_address(url):
    # Regular expression pattern to match Ethereum/BSC wallet addresses
    pattern = r'(?:0x)[0-9a-fA-F]{40}'
    # Find all matches in the URL
    matches = re.findall(pattern, url)
    # Return the first match (wallet address) if found, otherwise return None
    return matches[0] if matches else None

def exe_tx(tx: object, pk: str):
    signed_txn = w3.eth.account.sign_transaction(
        tx, pk)
    tx_hash = w3.eth.send_raw_transaction(
        signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    tx = w3.eth.get_transaction(tx_hash)

    print(tx)