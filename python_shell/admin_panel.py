# python_shell/admin_panel.py
"""
Admin panel: checks contract presence, mints initial plots (in batches),
sets ownership change fee, and inspects treasuries.
This CLI talks to on-chain contracts using web3.
"""

import json
from web3 import Web3
from .helpers import get_web3, account_from_key, load_json, save_json, to_xbgl_units, from_xbgl_units
from . import config

# ABI loader helper (expects compiled JSON artifacts in artifacts/ or supply ABI strings)
def load_abi(name):
    abi_path = f"../artifacts/{name}.json"
    try:
        with open(abi_path, "r") as f:
            j = json.load(f)
            return j.get("abi", j)  # allow raw abi or full artifact
    except FileNotFoundError:
        raise Exception(f"ABI for {name} not found at {abi_path}. Add compiled contract JSON to artifacts/")

class AdminPanel:
    def __init__(self):
        self.w3 = get_web3()
        self.account = account_from_key()
        self.tx_from = self.account.address

        # load ABIs and contract handles
        self.land_abi = load_abi("LandRegistry")
        self.treasury_abi = load_abi("Treasury")
        self.ownership_abi = load_abi("OwnershipDocs")

        self.land = self.w3.eth.contract(address=Web3.toChecksumAddress(config.CONTRACTS["LandRegistry"]), abi=self.land_abi)
        self.treasury = self.w3.eth.contract(address=Web3.toChecksumAddress(config.CONTRACTS["Treasury"]), abi=self.treasury_abi)
        self.docs = self.w3.eth.contract(address=Web3.toChecksumAddress(config.CONTRACTS["OwnershipDocs"]), abi=self.ownership_abi)

    def mint_initial_plots(self, start_id, count, area_m2, to_address):
        nonce = self.w3.eth.get_transaction_count(self.tx_from)
        tx = self.land.functions.mintPlots(start_id, count, area_m2, Web3.toChecksumAddress(to_address)).build_transaction({
            "from": self.tx_from,
            "nonce": nonce,
            "gas": 5000000,
            "gasPrice": self.w3.toWei("25", "gwei")
        })
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        print("Mint tx sent:", tx_hash.hex())
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Mint receipt:", receipt)

    def set_ownership_fee(self, xbgl_amount):
        units = to_xbgl_units(xbgl_amount)
        nonce = self.w3.eth.get_transaction_count(self.tx_from)
        tx = self.land.functions.setOwnershipChangeFee(units).build_transaction({
            "from": self.tx_from, "nonce": nonce, "gas": 200000, "gasPrice": self.w3.toWei("25", "gwei")
        })
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        print("Set fee tx:", tx_hash.hex())
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Ownership change fee updated.")

    def inspect_treasuries(self):
        oct, sar = self.treasury.functions.balances().call()
        print("Octavia treasury:", from_xbgl_units(oct), "xBGL")
        print("Sarakt treasury:", from_xbgl_units(sar), "xBGL")

    def issue_doc(self, plotId, owner_pubkey, docHash):
        nonce = self.w3.eth.get_transaction_count(self.tx_from)
        tx = self.docs.functions.issueDoc(plotId, owner_pubkey, docHash).build_transaction({
            "from": self.tx_from, "nonce": nonce, "gas": 200000, "gasPrice": self.w3.toWei("25", "gwei")
        })
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        print("Issue doc tx:", tx_hash.hex())
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Doc issued on-chain.")
