import os

from staking_sdk_py.signer_factory import Signer, LocalSigner, LedgerSigner
from src.logger import init_logging


def create_signer(config: dict) -> Signer:
    log = init_logging(config["log_level"].upper())
    staking_type = os.environ.get("STAKING_TYPE")
    if not staking_type:
        staking_type = config["staking"].get("type", "local").lower()
    if not staking_type:  # should never be here except for misconfigurations
        raise ValueError(
            "staking_type is required as STAKING_TYPE env var or in config file"
        )

    if staking_type == "local":
        log.debug(f"Initializing local signer")
        private_key = os.environ.get("FUNDED_ADDRESS_PRIVATE_KEY")
        if not private_key:
            private_key = config["staking"].get("funded_address_private_key")
        if not private_key:
            raise ValueError(
                "private_key is required as FUNDED_ADDRESS_PRIVATE_KEY env var or in config file"
            )
        log.debug(f"Local signer initialized")
        return LocalSigner(private_key)

    elif staking_type == "ledger":
        log.debug(f"Initializing ledger signer")
        derivation_path = os.environ.get("DERIVATION_PATH")
        if not derivation_path:
            derivation_path = config["staking"].get("derivation_path", "44'/60'/0'/0/0")
        if not derivation_path:  # should never be here except for misconfigurations
            raise ValueError(
                "derivation_path is required as DERIVATION_PATH env var or in config file"
            )
        log.debug(f"Ledger signer initialized")
        return LedgerSigner(derivation_path)

    else:
        raise ValueError(
            f"Invalid staking type: {staking_type}. Must be 'local' or 'ledger'"
        )
