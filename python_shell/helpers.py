# python_shell/helpers.py
import json
import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from . import config

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# web3 helpers
def get_web3():
    w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
    # if subnet uses PoA style
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

def account_from_key():
    return Account.from_key(config.PRIVATE_KEY)

# Convert xBGL human value to token units
def to_xbgl_units(amount_float):
    return int(amount_float * config.DECIMAL_FACTOR)

def from_xbgl_units(amount_int):
    return amount_int / config.DECIMAL_FACTOR
