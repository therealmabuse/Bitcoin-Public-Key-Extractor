# Bitcoin-Public-Key-Extractor
A fast and effective tool to extract Bitcoin public keys from the blockchain using the Alchemy API. 

Processes blocks in batches for efficiency and outputs results to organized files.

## Features ✨

- **Batch Processing**: Fetches and processes blocks in batches for optimal performance
- **Smart File Rotation**: Automatically creates new output files when reaching 25MB
- **Colorful UI**: Clean terminal interface with color-coded status messages
- **Resilient Design**: Built-in retry logic for failed requests
- **Flexible Scanning**: Start from any block height and scan any number of blocks

## Prerequisites 📋

- Python 3.8+
- Alchemy API account ([sign up here](https://dashboard.alchemy.com/))
- Bitcoin Mainnet access enabled in your Alchemy account

## Installation ⚙️

1. Clone the repository:
   ```bash
   git clone https://github.com/therealmabuse/bitcoin-pubkey-extractor.git
   cd bitcoin-pubkey-extractor
   pip install -r requirements.txt
   

## Configuration ⚡

Optional but recommended!
Create a .env file in the project root:
ini

ALCHEMY_API_KEY=your_api_key_here

## Usage 🚦

Run 
    
    python extractor.py

You'll be prompted to:

    Enter your Alchemy API key (if not in .env file)

    Specify starting block number (or press Enter for latest)

    Enter how many blocks to scan

## Output 📂

Public keys are saved in sequentially numbered files:
text

pulled_1.txt
pulled_2.txt
...

Each file contains one public key per line in hex format.

## Performance Tips ⚡

    Larger batch sizes process faster but may hit API limits

    Typical rate: 50-100 blocks per minute (varies by API tier)

    Monitor your Alchemy dashboard for usage statistics

## Troubleshooting 🛠️
Issue	Solution
API key not working	Verify key is correct and has Bitcoin Mainnet access

Connection errors	Check network connection and API endpoint

Empty output files	Try with smaller batch sizes (e.g., 20 blocks)

Rate limiting	Increase REQUEST_DELAY in code or upgrade API tier

## License 

## MIT License - See LICENSE file for details

If you find this tool useful, consider:

⭐ Starring this repository

🐛 Reporting issues

💻 Contributing improvements
