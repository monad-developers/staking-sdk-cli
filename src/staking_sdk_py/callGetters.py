from eth_abi.abi import decode
import staking_sdk_py.constants as constants
from staking_sdk_py.generateCalldata import (
    get_epoch,
    get_validator,
    get_delegator,
    get_withdrawal_request,
    get_consensus_valset,
    get_snapshot_valset,
    get_execution_valset,
    get_delegations,
    get_delegators
)
from web3 import Web3

def call_contract(w3, contract_address: str, calldata: str) -> bytes:
    """
    Calls a contract getter function and returns raw bytes.
    """
    tx = {
        "to": Web3.to_checksum_address(contract_address),
        "data": calldata,
    }
    result = w3.eth.call(tx)
    return result  # raw bytes


def call_getter(w3, getter_name: str, contract_address: str, *args) -> tuple:
    calldata_builder = {
        "get_epoch": lambda : get_epoch(),
        "get_validator": lambda val_id: get_validator(val_id),
        "get_delegator": lambda val_id, delegator: get_delegator(val_id, delegator),
        "get_withdrawal_request": lambda val_id, delegator, wid: get_withdrawal_request(val_id, delegator, wid),
        "get_consensus_valset": lambda idx: get_consensus_valset(idx),
        "get_snapshot_valset": lambda idx: get_snapshot_valset(idx),
        "get_execution_valset": lambda idx: get_execution_valset(idx),
        "get_delegations": lambda delegator_address, idx: get_delegations(delegator_address, idx),
        "get_delegators": lambda val_id, delegator_address: get_delegators(val_id, delegator_address),
    }

    if getter_name not in calldata_builder:
        raise ValueError(f"Unknown getter {getter_name}")

    calldata = calldata_builder[getter_name](*args)
    raw_result = call_contract(w3,contract_address, calldata)
    abi_types = constants.GETTER_ABIS.get(getter_name)
    if not abi_types:
        # return raw if ABI not defined
        return raw_result

    decoded = decode(abi_types, raw_result)
    return decoded
