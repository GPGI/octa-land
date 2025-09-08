# python_shell/city_panel.py
"""
City operator panel: sell primary plots (simulate primary sale), list for sale, buy from secondary.
This module demonstrates calls to LandRegistry functions.
"""
from web3 import Web3
import json
from .helpers import get_web3, account_from_key, load_json, save_json, to_xbgl_units, from_xbgl_units
from . import config

def load_abi(name):
    with open(f"../artifacts/{name}.json", "r") as f:
        j = json.load(f)
        return j.get("abi", j)

class CityPanel:
    def __init__(self):
        self.w3 = get_web3()
        self.account = account_from_key()
        self.tx_from = self.account.address
        self.land_abi = load_abi("LandRegistry")
        self.land = self.w3.eth.contract(address=Web3.toChecksumAddress(config.CONTRACTS["LandRegistry"]), abi=self.land_abi)

    def trigger_primary_sale(self, plotId, buyer_address):
        # buyer must have approved this LandRegistry contract for plotPrice
        # admin triggers buyPrimary by having buyer call buyPrimary; here we assume admin can call as wrapper (for demonstration)
        nonce = self.w3.eth.get_transaction_count(self.tx_from)
        tx = self.land.functions.buyPrimary(plotId).build_transaction({
            "from": self.tx_from, "nonce": nonce, "gas": 300000, "gasPrice": self.w3.toWei("25", "gwei")
        })
        signed = self.account.sign_transaction(tx)
        txh = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        print("Primary sale tx:", txh.hex())
        self.w3.eth.wait_for_transaction_receipt(txh)
        print("Primary sale complete for plot", plotId)

    def list_secondary(self, plotId, price_xbgl_float):
        price_units = to_xbgl_units(price_xbgl_float)
        nonce = self.w3.eth.get_transaction_count(self.tx_from)
        tx = self.land.functions.listPlotForSale(plotId, price_units).build_transaction({
            "from": self.tx_from, "nonce": nonce, "gas": 200000, "gasPrice": self.w3.toWei("25", "gwei")
        })
        signed = self.account.sign_transaction(tx)
        txh = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        print("Listing tx:", txh.hex())
        self.w3.eth.wait_for_transaction_receipt(txh)
        print("Plot listed for sale.")

    def buy_secondary(self, plotId):
        # buyer must approve salePrice + buyer commission to LandRegistry
        nonce = self.w3.eth.get_transaction_count(self.tx_from)
        tx = self.land.functions.buySecondary(plotId).build_transaction({
            "from": self.tx_from, "nonce": nonce, "gas": 400000, "gasPrice": self.w3.toWei("25", "gwei")
        })
        signed = self.account.sign_transaction(tx)
        txh = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        print("Buy secondary tx:", txh.hex())
        self.w3.eth.wait_for_transaction_receipt(txh)
        print("Secondary purchase executed.")
