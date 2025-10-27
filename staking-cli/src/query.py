from web3 import Web3
from staking_sdk_py.callGetters import call_getter
from src.logger import init_logging
from time import sleep 

def get_validator_info(config, val_id):
    # query validator information
    w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
    val_info = call_getter(w3, 'get_validator', config['contract_address'], val_id)
    return val_info

def validator_exists(val_info: tuple) -> bool:
    if val_info[10].hex() == "000000000000000000000000000000000000000000000000000000000000000000":
        return False
    return True

def get_validator_set(config: dict, type: str = "consensus") -> tuple:
    log = init_logging(config["log_level"])
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    is_done = False
    start_index = 0
    validator_set = []
    while not is_done:
        get_validator_set_response = call_getter(w3,f'get_{type}_valset', contract_address, start_index)
        is_done = get_validator_set_response[0]
        start_index = get_validator_set_response[1]
        for val_id in get_validator_set_response[2]:
            validator_set.append(val_id)
        sleep(0.1)
    log.debug(f"Validator Set: {validator_set}")
    return validator_set

def get_delegator_info(config: dict, val_id: int, delegator_address: str):
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    delegator_info = call_getter(w3,'get_delegator', contract_address, val_id, delegator_address)
    return delegator_info

def get_withdrawal_info(config: dict, validator_id: str, delegator_address: str, withdrawal_id: int):
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    withdrawal_request = call_getter(w3, 'get_withdrawal_request', contract_address, validator_id, delegator_address, withdrawal_id)
    return withdrawal_request

def get_delegators_list(config: dict, validator_id: int, start_address: str = "0x0000000000000000000000000000000000000000"):
    log = init_logging(config["log_level"])
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    is_done = False
    delegators = []
    while not is_done:
        get_delegators_response = call_getter(w3, 'get_delegators', contract_address, validator_id, start_address)
        is_done = get_delegators_response[0]
        start_address = get_delegators_response[1]
        log.debug(f"Fetched {len(get_delegators_response[2])} delegators, fetching more addresses = {is_done}")
        for address in get_delegators_response[2]:
            delegators.append(address)
        sleep(0.1)
    return delegators


def get_validators_list(config: dict, delegator_address: str):
    log = init_logging(config["log_level"])
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    is_done = False
    start_index = 0
    validators = []
    while not is_done:
        get_delegations_response = call_getter(w3, 'get_delegations', contract_address, delegator_address, start_index)
        is_done = get_delegations_response[0]
        start_index = get_delegations_response[1]
        log.debug(f"Fetched {len(get_delegations_response[2])} validators, fetching more validators = {is_done}")
        for validator in get_delegations_response[2]:
            validators.append(validator)
        sleep(0.1)
    return validators

def get_epoch_info(config: dict):
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    epoch_info = call_getter(w3,'get_epoch', contract_address)
    return epoch_info

def get_tx_by_hash(config: dict, tx_hash: str):
    rpc_url = config["rpc_url"]
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        tx = w3.eth.get_transaction(tx_hash)
        return tx
    except Exception as e:
        return e
