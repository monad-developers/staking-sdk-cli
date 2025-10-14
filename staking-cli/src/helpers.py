from typing import Union
from web3 import Web3
from src.logger import init_logging
from src.query import get_validator_info, validator_exists
from py_ecc.optimized_bls12_381 import curve_order
from rich.prompt import Prompt, Confirm


def wei(amount: int) -> int:
    """Convert MON to wei"""
    return amount * 1_000_000_000_000_000_000


def count_zeros(amount: int) -> int:
    """Count zeros so you can estimate amount"""
    count = 0
    for i in str(amount):
        if i == "0":
            count += 1
    return count


def is_valid_amount(amount: int, register=False) -> bool:
    try:
        amount = int(amount)
    except Exception:
        return False
    if register:
        if amount < 100_000:
            return False
    return True


def is_valid_bls_private_key(private_key: Union[int, str]) -> bool:
    """Validates a BLS12-381 private key."""
    if isinstance(private_key, str):
        try:
            # Convert hex string (with '0x' prefix) to integer
            key_int = int(private_key, 16)
        except ValueError:
            return False
    elif isinstance(private_key, int):
        key_int = private_key
    else:
        return False  # Invalid type

    # Apply modulo reduction if key is larger than curve order
    if key_int >= curve_order:
        key_int = key_int % curve_order

    return 0 < key_int < curve_order


def is_valid_secp256k1_private_key(hex_private_key: str) -> bool:
    """Validates a secp256k1 private key in hexadecimal format."""
    SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    if not isinstance(hex_private_key, str):
        return False

    # Remove 0x prefix if present
    if hex_private_key.startswith("0x"):
        hex_private_key = hex_private_key[2:]

    if len(hex_private_key) != 64:
        return False

    try:
        key_int = int(hex_private_key, 16)
    except ValueError:
        return False
    return 0 < key_int < SECP256K1_ORDER


def number_prompt(description: str, range: list = [], default: str = ""):
    if range:
        return Prompt.ask(
            f"\n{description}", show_choices=False, choices=range, default=default
        )
    else:
        return Prompt.ask(f"\n{description}", show_choices=False, default=default)


def key_prompt(config: dict, key_type: str):
    """Ask for private key and validate"""
    colors = config["colors"]
    log = init_logging(config["log_level"].upper())
    key = Prompt.ask(
        f"\n[{colors['primary_text']}]Enter [{colors['main']}]{key_type.capitalize()} Private Key[/] of the validator[/]"
    )
    # valdiate input
    if key_type == "secp":
        validation = is_valid_secp256k1_private_key(key)
    else:
        validation = is_valid_bls_private_key(key)

    if validation:
        return str(key)
    else:
        log.error(f"\nEnter a valid key, instead of: {key}")
        # ask for input again
        key = key_prompt(config, key_type)
        return key


def is_valid_address(address: str) -> bool:
    """Validates an Ethereum address by checking its format and EIP-55 checksum."""
    try:
        Web3.to_checksum_address(address)
        return True
    except Exception:
        # The function raises an error (e.g., ValueError) if the address is invalid.
        return False


def address_prompt(config: dict, address_description: str, default: str = "") -> str:
    log = init_logging(config["log_level"].upper())
    colors = config["colors"]
    if default:
        address = Prompt.ask(
            f"\n[{colors['primary_text']}]Enter [{colors['main']}]{address_description}[/] address[/]",
            default=default,
        )
    else:
        address = Prompt.ask(
            f"\n[{colors['primary_text']}]Enter [{colors['main']}]{address_description}[/] address[/]"
        )

    if is_valid_address(address):
        return address
    else:
        log.error(f"\nEnter a valid address, instead of {address}")
        address = address_prompt(config, address_description, default)
        return address


def val_id_prompt(config: dict) -> int:
    log = init_logging(config["log_level"].upper())
    colors = config["colors"]
    val_id = Prompt.ask(
        f"\n[{colors['primary_text']}]Enter [{colors['main']}]Validator ID[/][/]"
    )
    try:
        val_id = int(val_id)
    except:
        log.error(f"\nEnter a valid integer, instead of {val_id}")
        val_id = val_id_prompt(config)
    val_info = get_validator_info(config, val_id)
    if validator_exists(val_info):
        return val_id
    else:
        log.error(f"\nValidator with ID: {val_id} doesn't exist! Try again!")
        val_id = val_id_prompt(config)
        return val_id


def amount_prompt(config: dict, method: str = "", description: str = "") -> int:
    """Ask for amount to delegate/undelegate/withdraw"""
    colors = config["colors"]
    log = init_logging(config["log_level"].upper())
    amount = Prompt.ask(
        f"\n[{colors['primary_text']}]Enter an amount in [{colors['main']}]MON[/] {description}[/]"
    )
    try:
        amount = int(amount)
        if amount <= 0:
            log.error("\nEnter a value greater than 0")
            amount = amount_prompt(config, method)
            return amount
        if method == "add_validator":
            if amount < 100_000:
                log.error("\nMinimum Stake to add validator is 100,000 MON")
                amount = amount_prompt(config, method)
                return amount
        return amount
    except:
        log.error(f"\nEnter a valid integer amount! instead of {amount}")
        amount = amount_prompt(config, method)
        return amount


def confirmation_prompt(description: str, default: bool) -> bool:
    is_confirmed = Confirm.ask(
        f"\n[bold yellow]{description}[/]",
        default=default,  # Make the safe option the default
    )
    return is_confirmed
