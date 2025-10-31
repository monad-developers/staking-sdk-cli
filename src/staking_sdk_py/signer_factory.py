from abc import ABC, abstractmethod

from eth_account import Account
from eth_account.datastructures import SignedTransaction
from ledgerblue.comm import getDongle
from ledgereth.accounts import get_account_by_path
from ledgereth.objects import SignedTransaction as LedgerSignedTransaction
from ledgereth.transactions import Type2Transaction, sign_transaction
from rlp import encode
from web3 import Web3


class Signer(ABC):
    """
    Abstract base class for all signers.
    """

    @abstractmethod
    def get_address(self) -> str:
        pass

    @abstractmethod
    def sign_transaction(self, tx: dict) -> SignedTransaction:
        pass


class LocalSigner(Signer):
    """
    Signer implementation using a local private key.
    """

    def __init__(self, private_key: str):
        self.private_key_hex = (
            private_key[2:] if private_key.startswith("0x") else private_key
        )
        if len(self.private_key_hex) != 64:
            raise ValueError("Private key must be 32 bytes (64 hex characters)")
        self.account = Account.from_key(self.private_key_hex)
        self.address = Web3.to_checksum_address(self.account.address)

    def get_address(self) -> str:
        return self.address

    def sign_transaction(self, tx: dict) -> SignedTransaction:
        return self.account.sign_transaction(tx)


def strip_0x(hex_str: str) -> str:
    return hex_str[2:] if hex_str.startswith("0x") else hex_str


class LedgerSigner(Signer):
    """
    Signer implementation using a Ledger hardware wallet.

    Args:
        derivation_path (str): BIP32 derivation path (e.g. default "44'/60'/0'/0/0")
    """

    def __init__(self, derivation_path: str = "44'/60'/0'/0/0"):
        self.dongle = getDongle()
        if derivation_path.startswith("m/"):
            derivation_path = derivation_path[2:]
        self.derivation_path = derivation_path
        self.ledger_account = get_account_by_path(self.derivation_path, self.dongle)
        self.address = Web3.to_checksum_address(self.ledger_account.address)

    def get_address(self) -> str:
        return self.address

    def sign_transaction(self, tx: dict) -> SignedTransaction:

        # Convert tx dict to ledgereth Type2Transaction
        ledger_tx = Type2Transaction(
            destination=bytes.fromhex(strip_0x(tx["to"])),
            amount=tx["value"],
            gas_limit=tx["gas"],
            data=bytes.fromhex(strip_0x(tx["data"])) if tx.get("data") else b"",
            nonce=tx["nonce"],
            chain_id=tx["chainId"],
            max_priority_fee_per_gas=tx["maxPriorityFeePerGas"],
            max_fee_per_gas=tx["maxFeePerGas"],
            access_list=None,
        )

        signed: LedgerSignedTransaction = sign_transaction(
            ledger_tx, self.derivation_path, self.dongle
        )

        # Convert ledgereth SignedTransaction to raw bytes and RLP encode
        raw_tx = signed.transaction_type.to_byte() + encode(signed, type(signed))

        # Return eth_account SignedTransaction
        return SignedTransaction(
            raw_transaction=raw_tx,
            hash=Web3.keccak(raw_tx),
            r=signed.sender_r,
            s=signed.sender_s,
            v=signed.y_parity,
        )
