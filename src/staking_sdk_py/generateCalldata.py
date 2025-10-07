from blake3 import blake3
from eth_keys import keys
from py_ecc.bls import G2ProofOfPossession as bls
from typing import Union

import staking_sdk_py.constants as constants
import staking_sdk_py.keyGenerator as keyGenerator

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

    return "0x" + constants.ADD_VALIDATOR_SELECTOR + encode(['bytes', 'bytes', 'bytes'], [payload, secp_sig, bls_sig]).hex()


def strip_0x(s: str) -> str:
    return s[2:] if s.startswith("0x") else s


def _address_to_bytes(address: str) -> bytes:
    """Convert a hex address to a 20-byte representation for ABI encoding."""
    if not isinstance(address, str):
        raise TypeError("Address must be provided as a string")

    sanitized = strip_0x(address)
    if len(sanitized) != 40:
        raise ValueError("Address must be 20 bytes (40 hex characters)")

    try:
        return bytes.fromhex(sanitized)
    except ValueError as exc:
        raise ValueError("Address contains non-hex characters") from exc

def delegate(validator_id: Union[int, str]) -> str:
    return "0x" + constants.DELEGATE_SELECTOR + encode(['uint64'], [validator_id]).hex()

def undelegate(validator_id: Union[int, str], amount: Union[int, str], withdraw_id: int) -> str:
    return "0x" + constants.UNDELEGATE_SELECTOR + encode(['uint64', 'uint256', 'uint8'], [validator_id, amount, withdraw_id]).hex()

def withdraw(validator_id: Union[int, str], withdraw_id: int) -> str:
    return "0x" + constants.WITHDRAW_SELECTOR + encode(['uint64', 'uint8'], [validator_id, withdraw_id]).hex()

def compound(validator_id: Union[int, str]) -> str:
    return "0x" + constants.COMPOUND_SELECTOR + encode(['uint64'], [validator_id]).hex()

def claim_rewards(validator_id: Union[int, str]) -> str:
    return "0x" + constants.CLAIM_REWARDS_SELECTOR + encode(['uint64'], [validator_id]).hex()

def change_commission(validator_id: Union[int, str], commission: int) -> str:
    return "0x" + constants.CHANGE_COMMISSION_SELECTOR + encode(['uint64', 'uint256'], [validator_id, commission]).hex()

def get_epoch() -> str:
    return "0x" + constants.GET_EPOCH_SELECTOR

def get_validator(validator_id: Union[int, str]) -> str:
    return "0x" + constants.GET_VALIDATOR_SELECTOR + encode(['uint64'], [validator_id]).hex()

def get_delegator(validator_id: Union[int, str], delegator_address: str) -> str:
    address_bytes = _address_to_bytes(delegator_address)
    return "0x" + constants.GET_DELEGATOR_SELECTOR + encode(['uint64', 'address'], [validator_id, address_bytes]).hex()

def get_withdrawal_request(validator_id: Union[int, str], delegator_address: str, withdrawal_id: int) -> str:
    address_bytes = _address_to_bytes(delegator_address)
    return "0x" + constants.GET_WITHDRAWAL_REQUEST_SELECTOR + encode(['uint64', 'address', 'uint8'], [int(validator_id), address_bytes, withdrawal_id]).hex()

def get_consensus_valset(index: Union[int, str]) -> str:
    return "0x" + constants.GET_CONSENSUS_VALSET_SELECTOR + encode(['uint64'], [index]).hex()

def get_snapshot_valset(index: Union[int, str]) -> str:
    return "0x" + constants.GET_SNAPSHOT_VALSET_SELECTOR + encode(['uint64'], [index]).hex()

def get_execution_valset(index: Union[int, str]) -> str:
    return "0x" + constants.GET_EXECUTION_VALSET_SELECTOR + encode(['uint64'], [index]).hex()

def get_delegations(delegator_address: str, index: int) -> str:
    address_bytes = _address_to_bytes(delegator_address)
    return "0x" + constants.GET_DELEGATIONS_SELECTOR + encode(['address','uint64'], [address_bytes, index]).hex()

def get_delegators(val_id: int, delegator_address: str) -> str:
    address_bytes = _address_to_bytes(delegator_address)
    return "0x" + constants.GET_DELEGATORS_SELECTOR + encode(['uint64', 'address'], [val_id, address_bytes]).hex()
