import json
from solcx import compile_standard, install_solc
from web3 import Web3
from config import w3, PRIVATE_KEY, WALLET_ADDRESS, CHAIN_ID, TOKEN_ADDRESS

def deploy_contract():
    if TOKEN_ADDRESS:
        print(f"Contract already deployed at: {TOKEN_ADDRESS}")
        return TOKEN_ADDRESS

    # Read solidity source
    with open("contracts/LandRegistry.sol", "r") as file:
        source_code = file.read()

    # Install compiler
    install_solc("0.8.20")

    # Compile
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"LandRegistry.sol": {"content": source_code}},
            "settings": {
                "outputSelection": {"*": {"*": ["abi", "metadata", "evm.bytecode"]}}
            },
        },
        solc_version="0.8.20",
    )

    # Save ABI
    abi = compiled_sol["contracts"]["LandRegistry.sol"]["LandRegistry"]["abi"]
    bytecode = compiled_sol["contracts"]["LandRegistry.sol"]["LandRegistry"]["evm"]["bytecode"]["object"]

    with open("out/LandRegistry.sol/LandRegistry.json", "w") as f:
        json.dump({"abi": abi, "bytecode": bytecode}, f)

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    construct_txn = contract.constructor(WALLET_ADDRESS).build_transaction({
        "from": WALLET_ADDRESS,
        "nonce": w3.eth.get_transaction_count(WALLET_ADDRESS),
        "chainId": CHAIN_ID,
        "gas": 3000000,
        "gasPrice": w3.eth.gas_price,
    })

    signed_txn = w3.eth.account.sign_transaction(construct_txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Deployed at: {receipt.contractAddress}")
    return receipt.contractAddress

if __name__ == "__main__":
    deploy_contract()
