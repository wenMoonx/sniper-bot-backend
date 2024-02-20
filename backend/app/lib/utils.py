import re

def extract_wallet_address(url):
    # Regular expression pattern to match Ethereum/BSC wallet addresses
    pattern = r'(?:0x)[0-9a-fA-F]{40}'
    # Find all matches in the URL
    matches = re.findall(pattern, url)
    # Return the first match (wallet address) if found, otherwise return None
    return matches[0] if matches else None
