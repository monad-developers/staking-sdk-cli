import struct
import requests
from web3 import Web3
from staking_sdk_py.callGetters import call_getter
from src.logger import init_logging


def get_validator_info(config, val_id):
    # query validator information
    w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
    val_info = call_getter(w3, "get_validator", config["contract_address"], val_id)
    return val_info


def validator_exists(val_info: tuple) -> bool:
    if (
        val_info[10].hex()
        == "000000000000000000000000000000000000000000000000000000000000000000"
    ):
        return False
    return True


def get_validator_set(config: dict, type: str = "consensus") -> tuple:
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    validator_set = call_getter(w3, f"get_{type}_valset", contract_address, 0)
    return validator_set[2]


def get_delegator_info(config: dict, val_id: int, delegator_address: str):
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    delegator_info = call_getter(
        w3, "get_delegator", contract_address, val_id, delegator_address
    )
    return delegator_info


def get_withdrawal_info(
    config: dict, validator_id: str, delegator_address: str, withdrawal_id: int
):
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    withdrawal_request = call_getter(
        w3,
        "get_withdrawal_request",
        contract_address,
        validator_id,
        delegator_address,
        withdrawal_id,
    )
    return withdrawal_request


def get_delegators_list(config: dict, validator_id: int):
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    delegators = call_getter(
        w3,
        "get_delegators",
        contract_address,
        validator_id,
        "0x0000000000000000000000000000000000000000",
    )
    return delegators


def get_validators_list(config: dict, delegator_address: str):
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    validators_result = call_getter(
        w3, "get_delegations", contract_address, delegator_address, 0
    )
    return validators_result


def get_epoch_info(config: dict):
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    epoch_info = call_getter(w3, "get_epoch", contract_address)
    return epoch_info


def get_tx_by_hash(config: dict, tx_hash: str):
    rpc_url = config["rpc_url"]
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        tx = w3.eth.get_transaction(tx_hash)
        return tx
    except Exception as e:
        return e


def eth_get_storage_at(
    config: dict, slot_key: bytes, block: str = "latest", timeout=15
) -> bytes:
    rpc_url = config["rpc_url"]
    assert len(slot_key) == 32
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getStorageAt",
        "params": [
            "0x0000000000000000000000000000000000001000",
            "0x" + slot_key.hex(),
            block,
        ],
    }
    r = requests.post(rpc_url, json=payload, timeout=timeout)
    result = r.json()["result"].replace("0x", "")
    return bytes.fromhex(result)


def get_val_id_from_secp_pubkey(config: dict, eth_address: str) -> int:
    VAL_ID_SECP_NAMESPACE = 0x06
    slot_key = struct.pack(
        ">B20s11s", VAL_ID_SECP_NAMESPACE, bytes.fromhex(eth_address[2:]), b"\x00" * 11
    )
    slot_data = eth_get_storage_at(config, slot_key)
    val_id = int.from_bytes(slot_data[:8], "big")
    return val_id
