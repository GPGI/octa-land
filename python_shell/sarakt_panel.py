# python_shell/sarakt_panel.py
"""
Planet (Sarakt) operator panel: shows planet-wide metrics, can withdraw sarakt funds.
"""
from web3 import Web3
import json
from .helpers import get_web3, account_from_key, load_json, save_json, to_xbgl_units, from_xbgl_units
from . import config

def load_abi(name):
    with open(f"../artifacts/{name}.json", "r") as f:
        j = json.load(f)
        return j.get("abi", j)

class SaraktPanel:
    def __init__(self):
        self.w3 = get_web3()
        self.account = account_from_key()
        self.tx_from = self.account.address
        self.treasury_abi = load_abi("Treasury")
        self.treasury = self.w3.eth.contract(address=Web3.toChecksumAddress(config.CONTRACTS["Treasury"]), abi=self.treasury_abi)

    def show_balances(self):
        oct, sar = self.treasury.functions.balances().call()
        print("Octavia:", from_xbgl_units(oct), "xBGL")
        print("Sarakt:", from_xbgl_units(sar), "xBGL")

    def withdraw_sarakt(self, to_addr, amount_xbgl):
        amount_units = to_xbgl_units(amount_xbgl)
        nonce = self.w3.eth.get_transaction_count(self.tx_from)
        tx = self.treasury.functions.withdrawSarakt(Web3.toChecksumAddress(to_addr), amount_units).build_transaction({
            "from": self.tx_from, "nonce": nonce, "gas": 200000, "gasPrice": self.w3.toWei("25", "gwei")
        })
        signed = self.account.sign_transaction(tx)
        txh = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        print("Withdraw tx:", txh.hex())
        self.w3.eth.wait_for_transaction_receipt(txh)
        print("Withdrawal executed.")
