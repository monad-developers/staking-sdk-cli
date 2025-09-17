from blake3 import blake3
from eth_keys import keys
import staking_sdk_py.constants as constants
import staking_sdk_py.keyGenerator as keyGenerator
from typing import Union
import eth_abi


from blake3 import blake3
from eth_keys import keys
from py_ecc.bls import G2ProofOfPossession as bls
from py_ecc.optimized_bls12_381 import curve_order

from eth_abi import encode

def add_validator(
    k: "keyGenerator.KeyGenerator",
    amount: int,
    auth_address: str,
    commission: int = 0
) -> str:
    secp_pub_key = k.pub_secp_key()
    bls_pub_key = k.pub_bls_key()
    auth_address_bytes = bytes.fromhex(strip_0x(auth_address))

    secp_priv_key = k.priv_secp_key()
    bls_privkey = k.priv_bls_key()

    # Build payload (everything except the signatures)
    payload_parts = [
        secp_pub_key,
        bls_pub_key,
        auth_address_bytes,
        int(amount).to_bytes(32, byteorder='big'),
        int(commission).to_bytes(32, byteorder='big'),
    ]
    payload = b''.join(payload_parts)

    secp_sig = secp_priv_key.sign_msg_hash_non_recoverable(blake3(payload).digest()).to_bytes()
    bls_sig = bls.Sign(bls_privkey, payload)

    return "0x" + constants.ADD_VALIDATOR_SELECTOR + eth_abi.encode(['bytes', 'bytes', 'bytes'], [payload, secp_sig, bls_sig]).hex()


def strip_0x(s: str) -> str:
    return s[2:] if s.startswith("0x") else s

def delegate(validator_id: Union[int, str]) -> str:
    return "0x" + constants.DELEGATE_SELECTOR + eth_abi.encode(['uint64'], [validator_id]).hex()

def undelegate(validator_id: Union[int, str], amount: Union[int, str], withdraw_id: int) -> str:
    return "0x" + constants.UNDELEGATE_SELECTOR + eth_abi.encode(['uint64', 'uint256', 'uint8'], [validator_id, amount, withdraw_id]).hex()

def withdraw(validator_id: Union[int, str], withdraw_id: int) -> str:
    return "0x" + constants.WITHDRAW_SELECTOR + eth_abi.encode(['uint64', 'uint8'], [validator_id, withdraw_id]).hex()

def compound(validator_id: Union[int, str]) -> str:
    return "0x" + constants.COMPOUND_SELECTOR + eth_abi.encode(['uint64'], [validator_id]).hex()

def claim_rewards(validator_id: Union[int, str]) -> str:
    return "0x" + constants.CLAIM_REWARDS_SELECTOR + eth_abi.encode(['uint64'], [validator_id]).hex()

def get_epoch() -> str:
    return "0x" + constants.GET_EPOCH_SELECTOR

def get_validator(validator_id: Union[int, str]) -> str:
    return "0x" + constants.GET_VALIDATOR_SELECTOR + eth_abi.encode(['uint64'], [validator_id]).hex()

def get_delegator(validator_id: Union[int, str], delegator_address: str) -> str:
    address_hex = strip_0x(delegator_address)
    return "0x" + constants.GET_DELEGATOR_SELECTOR + eth_abi.encode(['uint64', 'address'], [validator_id, address_hex]).hex()

def get_withdrawal_request(validator_id: Union[int, str], delegator_address: str, withdrawal_id: int) -> str:
    address_hex = strip_0x(delegator_address)
    return "0x" + constants.GET_WITHDRAWAL_REQUEST_SELECTOR + eth_abi.encode(['uint64', 'address', 'uint8'], [int(validator_id), address_hex, withdrawal_id]).hex()

def get_consensus_valset(index: Union[int, str]) -> str:
    return "0x" + constants.GET_CONSENSUS_VALSET_SELECTOR + eth_abi.encode(['uint64'], [index]).hex()

def get_snapshot_valset(index: Union[int, str]) -> str:
    return "0x" + constants.GET_SNAPSHOT_VALSET_SELECTOR + eth_abi.encode(['uint64'], [index]).hex()

def get_execution_valset(index: Union[int, str]) -> str:
    return "0x" + constants.GET_EXECUTION_VALSET_SELECTOR + eth_abi.encode(['uint64'], [index]).hex()

def get_delegations(delegator_address: str, index: int) -> str:
    address_hex = delegator_address[2:] if delegator_address.startswith("0x") else delegator_address
    return "0x" + constants.GET_DELEGATIONS_SELECTOR + eth_abi.encode(['address','uint64'], [address_hex, index]).hex()

def get_delegators(val_id: int, delegator_address: str) -> str:
    address_hex = delegator_address[2:] if delegator_address.startswith("0x") else delegator_address
    return "0x" + constants.GET_DELEGATORS_SELECTOR + eth_abi.encode(['uint64', 'address'], [val_id, address_hex]).hex()
