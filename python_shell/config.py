# python_shell/config.py
# Edit these values to your environment before running the shell.
# RPC / contract addresses / private key must be set.

RPC_URL = "https://your-avalanche-subnet-rpc"  # change
CHAIN_ID = 43114  # example Avalanche mainnet chain id; change if using custom subnet
PRIVATE_KEY = "0x..."  # admin private key (use an env var in production)

# Deployed contract addresses (fill after deployment)
CONTRACTS = {
    "xBGL": "0xYourExistingxBGLAddress",
    "Treasury": "0xTreasuryAddress",
    "LandRegistry": "0xLandRegistryAddress",
    "Mortgage": "0xMortgageAddress",
    "OwnershipDocs": "0xOwnershipDocsAddress"
}

# local data paths
DATA_DIR = "../data"
PLOTS_FILE = DATA_DIR + "/plots.json"
TREASURY_FILE = DATA_DIR + "/treasury.json"
MORTGAGES_FILE = DATA_DIR + "/mortgages.json"
POPULATION_FILE = DATA_DIR + "/population.json"

# smallest unit handling: xBGL token decimals (usually 18)
TOKEN_DECIMALS = 18
DECIMAL_FACTOR = 10 ** TOKEN_DECIMALS
