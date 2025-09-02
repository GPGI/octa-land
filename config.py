from web3 import Web3

# RPC URL for your blockchain node
RPC_URL = "http://151.237.142.106:9650/ext/bc/C/rpc"

# Owner wallet private key (Admin)
PRIVATE_KEY = "56289e99c94b6912bfc12adc093c9b51124f0dc54ac7a766b2bc5ccf558d8027"

# Chain ID for Avalanche
# Fuji = 43113, Mainnet = 43114, Local = 1337
CHAIN_ID = 1337

# Contract address (filled after deploy)
TOKEN_ADDRESS = "0xBBfCE55AD100b5bEd880083fCE366120347Af872"

# Web3 instance
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Wallet from private key
account = w3.eth.account.from_key(PRIVATE_KEY)
WALLET_ADDRESS = account.address

# Example recipient (for testing transfers)
RECIPIENT_ADDRESS = "0x2D5D2F3EA28942037d7556224Bdc3b49a493E5A0"

# ABI file path
ABI_PATH = "/home/hades/Desktop/projects/octavia-land/out/LandRegistry.sol/LandRegistry.json"

# Land registry defaults
LAND_PRICE_BGL = 400
LAND_SIZE_SQM = 500

# CSV storage
PENDING_TX_FILE = "data/pending_requests.csv"
MINTED_TX_FILE = "data/minted_lands.csv"