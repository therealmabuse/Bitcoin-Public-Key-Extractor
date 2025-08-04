import requests
import time
import os
from typing import List, Optional
from colorama import init, Fore, Style

import os
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    
# Initialize colorama
init()

# ASCII Art Logo with RGB colors
LOGO = f"""
{Fore.RED}██████ Bitcoin 
{Fore.GREEN}██████ Public Key
{Fore.BLUE}██████ Extractor
{Fore.GREEN}██████ 2025
{Fore.CYAN}██████ Version 2.2
{Fore.GREEN}██████ by MΔBUSΞ
{Style.RESET_ALL}{Fore.WHITE} {Style.RESET_ALL}
"""

HEADERS = {'Content-Type': 'application/json'}

# Constants
BATCH_SIZE = 50  # Number of blocks to request in each batch
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB in bytes
OUTPUT_PREFIX = "pulled"
REQUEST_DELAY = 5.0  # Delay between batch requests to avoid rate limiting
MAX_RETRIES = 3  # Maximum number of retry attempts for failed requests
RETRY_DELAY = 5  # Delay between retries in seconds

def display_logo():
    """Display the colorful logo"""
    print(LOGO)
    print(f"{Fore.WHITE} {Style.RESET_ALL}\n")

def get_alchemy_api_key() -> str:
    """Prompt user for Alchemy API key"""
    print(f"{Fore.YELLOW}Please enter your Alchemy API key:{Style.RESET_ALL}")
    api_key = input("> ").strip()
    while not api_key:
        print(f"{Fore.RED}API key cannot be empty!{Style.RESET_ALL}")
        api_key = input("> ").strip()
    return api_key

def batch_rpc_request(methods_params: List[tuple], rpc_url: str) -> List[dict]:
    """Make a batch JSON-RPC request"""
    payload = [
        {
            "jsonrpc": "2.0",
            "id": f"req-{i}",
            "method": method,
            "params": params
        }
        for i, (method, params) in enumerate(methods_params)
    ]
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(rpc_url, json=payload, headers=HEADERS)
            response.raise_for_status()
            results = response.json()
            
            # Sort results by request ID to maintain order
            if isinstance(results, list):
                return sorted(results, key=lambda x: int(x['id'].split('-')[1]))
            return [results]  # Handle single response
        except (requests.exceptions.RequestException, ValueError) as e:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(RETRY_DELAY * (attempt + 1))
    return []

def get_block_hashes_batch(heights: List[int], rpc_url: str) -> List[str]:
    """Get multiple block hashes in one batch request"""
    methods_params = [("getblockhash", [height]) for height in heights]
    results = batch_rpc_request(methods_params, rpc_url)
    return [result['result'] for result in results]

def get_blocks_batch(block_hashes: List[str], rpc_url: str) -> List[dict]:
    """Get multiple blocks with verbosity 2 in one batch request"""
    methods_params = [("getblock", [hash, 2]) for hash in block_hashes]
    results = batch_rpc_request(methods_params, rpc_url)
    return [result['result'] for result in results]

def extract_pubkeys_from_input(vin) -> Optional[str]:
    """Extract public key from transaction input"""
    if "coinbase" in vin:
        return None
    if "scriptSig" not in vin or not vin["scriptSig"].get("asm"):
        return None

    asm = vin["scriptSig"]["asm"].split()
    if len(asm) >= 2:
        pubkey = asm[-1]
        if pubkey.startswith(("02", "03", "04")):  # Compressed or uncompressed pubkey
            return pubkey
    return None

def process_blocks_batch(blocks: List[dict]) -> List[str]:
    """Process a batch of blocks to extract pubkeys"""
    pubkeys = []
    for block in blocks:
        for tx in block["tx"]:
            for vin in tx["vin"]:
                pk = extract_pubkeys_from_input(vin)
                if pk:
                    pubkeys.append(pk)
    return pubkeys

def get_next_output_filename() -> str:
    """Generate sequential output filenames"""
    index = 1
    while True:
        filename = f"{OUTPUT_PREFIX}_{index}.txt"
        if not os.path.exists(filename):
            return filename
        index += 1

def get_user_start_block(rpc_url: str) -> int:
    """Get starting block from user input"""
    try:
        latest_block = batch_rpc_request([("getblockcount", [])], rpc_url)[0]['result']
    except Exception as e:
        print(f"{Fore.RED}Error getting latest block: {e}{Style.RESET_ALL}")
        latest_block = 800000  # Fallback block height
        
    print(f"\n{Fore.CYAN}Current blockchain height: {latest_block}{Style.RESET_ALL}")
    
    while True:
        try:
            start_block = input(f"{Fore.YELLOW}Enter block number to start from (or press Enter for latest block): {Style.RESET_ALL}").strip()
            if not start_block:
                return latest_block
            
            start_block = int(start_block)
            if start_block < 0:
                print(f"{Fore.RED}Block number cannot be negative{Style.RESET_ALL}")
                continue
            if start_block > latest_block:
                print(f"{Fore.RED}Block number cannot exceed current height ({latest_block}){Style.RESET_ALL}")
                continue
            return start_block
        except ValueError:
            print(f"{Fore.RED}Please enter a valid block number{Style.RESET_ALL}")

def main():
    display_logo()
    
    # Get API key from user
    api_key = get_alchemy_api_key()
    rpc_url = f"https://bitcoin-mainnet.g.alchemy.com/v2/{api_key}"
    
    # Get scan parameters
    start_block = get_user_start_block(rpc_url)
    blocks_to_scan = int(input(f"{Fore.YELLOW}How many blocks to scan? {Style.RESET_ALL}"))
    
    current_file = get_next_output_filename()
    current_size = 0
    total_pubkeys = 0

    print(f"\n{Fore.GREEN}Starting scan from block {start_block} (scanning {blocks_to_scan} blocks)...{Style.RESET_ALL}")

    with open(current_file, "w") as f:
        pass  # Initialize empty file

    for batch_start in range(start_block, start_block - blocks_to_scan, -BATCH_SIZE):
        batch_end = max(batch_start - BATCH_SIZE + 1, start_block - blocks_to_scan + 1)
        batch_heights = list(range(batch_start, batch_end - 1, -1))
        
        print(f"\n{Fore.BLUE}Processing blocks {batch_start} to {batch_end}...{Style.RESET_ALL}")
        
        try:
            # Get all block hashes for this batch
            block_hashes = get_block_hashes_batch(batch_heights, rpc_url)
            
            # Get all blocks for this batch
            blocks = get_blocks_batch(block_hashes, rpc_url)
            
            # Process all blocks in this batch
            pubkeys = process_blocks_batch(blocks)
            
            # Write to file
            with open(current_file, "a") as f:
                for pk in pubkeys:
                    f.write(pk + "\n")
                    current_size += len(pk) + 1  # +1 for newline
                    total_pubkeys += 1
                    
                    # Rotate file if needed
                    if current_size >= MAX_FILE_SIZE:
                        f.flush()
                        current_file = get_next_output_filename()
                        current_size = 0
                        print(f"{Fore.MAGENTA}  → Created new output file: {current_file}{Style.RESET_ALL}")
            
            print(f"{Fore.GREEN}  Processed {len(blocks)} blocks, found {len(pubkeys)} pubkeys in this batch{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error processing blocks {batch_start}-{batch_end}: {str(e)}{Style.RESET_ALL}")
            continue
        
        time.sleep(REQUEST_DELAY)  # Rate limiting

    print(f"\n{Fore.GREEN}✔ Done. Extracted {total_pubkeys} public keys total{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Output files: {OUTPUT_PREFIX}_*.txt{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
