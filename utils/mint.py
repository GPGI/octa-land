import json
from config import w3, PRIVATE_KEY, WALLET_ADDRESS, CHAIN_ID, ABI_PATH, TOKEN_ADDRESS, RECIPIENT_ADDRESS

def mint_land(to_address):
    with open(ABI_PATH, "r") as f:
        contract_json = json.load(f)

    abi = contract_json["abi"]
    contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=abi)

    # estimate gas dynamically + safety buffer
    gas_estimate = contract.functions.mintLand(to_address).estimate_gas({
        "from": WALLET_ADDRESS
    })
    gas_with_buffer = int(gas_estimate * 1.2)

    txn = contract.functions.mintLand(to_address).build_transaction({
        "from": WALLET_ADDRESS,
        "nonce": w3.eth.get_transaction_count(WALLET_ADDRESS),
        "chainId": CHAIN_ID,
        "gas": gas_with_buffer,
        "gasPrice": w3.eth.gas_price,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Minted land for {to_address}, tx: {tx_hash.hex()}")
    return receipt

if __name__ == "__main__":
    mint_land (RECIPIENT_ADDRESS)