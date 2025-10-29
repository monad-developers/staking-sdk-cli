import warnings
from web3 import Web3
from staking_sdk_py.generateCalldata import add_validator
from staking_sdk_py.generateTransaction import send_transaction
from staking_sdk_py.keyGenerator import KeyGenerator
from staking_sdk_py.signer_factory import Signer
from rich.console import Console
from rich.prompt import Confirm
from rich.prompt import Prompt
from rich.panel import Panel
from rich.json import JSON
from rich.table import Table
from src.logger import init_logging
from src.helpers import (
    count_zeros,
    amount_prompt,
    key_prompt,
    address_prompt,
    wei,
    is_valid_secp256k1_private_key,
    is_valid_bls_private_key,
    is_valid_address,
    is_valid_amount,
)

console = Console()


def register_validator(config: dict, signer: Signer):
    log = init_logging(config["log_level"].upper())
    # Get privkeys of Validators
    secp_privkey_hex = key_prompt(config, key_type="secp")
    bls_privkey_hex = key_prompt(config, key_type="bls")

    # Generate the pubkeys and address
    try:
        keygen = KeyGenerator.from_keys(
            secp_private_key=secp_privkey_hex, bls_private_key=bls_privkey_hex
        )
        secp_pubkey = keygen.pub_secp_key()
        bls_pubkey = keygen.pub_bls_key()
    except Exception as e:
        log.error(
            f"Key derivation failed: Your keys fall in the correct curve order but are incompatible with the cryptographic scheme: {e}"
        )
        return

    # from config
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    funded_address = signer.get_address()
    amount = wei(
        amount_prompt(
            config,
            method="add_validator",
            description="to stake to validator (min 100k MON to register validator)",
        )
    )
    auth_address = address_prompt(
        config, address_description="Authorized Address", default=funded_address
    )

    table = Table(
        show_header=False,
        title="Staking Script Inputs",
        title_style="red bold",
        expand=True,
        show_lines=True,
        # leading=True
    )

    table.add_column("Inputs")
    table.add_column("Values")
    table.add_row(
        "[cyan]Input [bold red]SECP Private Key[/bold red] (Hex String):[/]",
        f"[green]{secp_privkey_hex}[/]",
    )
    table.add_row(
        "[cyan]Input [bold red]BLS Private Key[/bold red] (Hex String):[/]",
        f"[green]{bls_privkey_hex}[/]",
    )
    table.add_row(
        "[cyan]Amount to [bold red]stake[/] while adding validator:[/]",
        f"[green]{amount} (contains {count_zeros(amount)} zeros)[/]",
    )
    table.add_row(
        "[cyan][bold red]Authorized Address[/] for delegation:[/]",
        f"[green]{auth_address}[/]",
    )
    table.add_row(
        "[cyan][bold red]Funded Address[/] to use for tx:[/]",
        f"[green]{funded_address}[/]",
    )
    table.add_row("[cyan][bold red]RPC[/] to use for tx:[/]", f"[green]{rpc_url}[/]")
    table.add_row(
        "[cyan][bold red]Staking Contract Address[/] for the network:[/]",
        f"[green]{contract_address}[/]",
    )
    console.print(table)

    derived_panel = Panel(
        f"""
    [cyan]SECP Public key:[/] [green]{secp_pubkey.hex()}[/]\n
    [cyan]BLS Public key:[/] [green]{bls_pubkey.hex()}[/]\n
    """,
        title="[bold red]Derived Public Keys[/]",
        border_style="red",
        padding=(1, 2),
    )
    console.print(derived_panel)

    # Verify inputs and derivations
    is_confirmed = Confirm.ask(
        "[bold yellow]Do the derived public keys match? (make sure that the private keys were recovered using monad-keystore) [/]",
        default=False,  # Make the safe option the default
    )

    # Verify inputs and derivations
    if is_confirmed:
        pass
    else:
        return

    # Calldata for tx
    add_validator_call_data = add_validator(keygen, amount, auth_address)
    if config["log_level"] == "debug":
        console.print(add_validator_call_data)

    # send tx
    try:
        tx_hash = send_transaction(
            w3,
            signer,
            contract_address,
            add_validator_call_data,
            chain_id,
            amount,
            gas_limit=2_000_000,
        )
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        console.print(f"Error! while trying to send tx: {e}")
        return

    # Create formatted transaction summary
    tx_table = Table(title="Transaction Results", show_header=False, expand=True)
    tx_table.add_column("Field", style="cyan")
    tx_table.add_column("Value", style="green")
    tx_table.add_row("Status", "✅ Success" if receipt.status == 1 else "❌ Failed")
    tx_table.add_row("Transaction Hash", "0x" + receipt.transactionHash.hex())
    tx_table.add_row("Block Number", str(receipt.blockNumber))
    tx_table.add_row("Gas Used", f"{receipt.gasUsed:,}")
    tx_table.add_row("From", receipt["from"])
    tx_table.add_row("To (Contract)", receipt.to)
    console.print(tx_table)

    get_validator_registration_event(config, receipt)


def register_validator_cli(
    config: dict, signer: Signer, secp_privkey: str, bls_privkey: str, auth_address: str, amount: int
):
    log = init_logging(config["log_level"].upper())

    # Input validation
    try:
        if not is_valid_bls_private_key(bls_privkey):
            log.error("Key validation failed! Verify bls key")
            return
        if not is_valid_secp256k1_private_key(secp_privkey):
            log.error("Key validation failed! Verify secp key")
            return
        if not is_valid_address(auth_address):
            log.error("Address validation failed! Verify auth address")
            return
        if not is_valid_amount(amount, register=True):
            log.error(
                "The amount enter was invalid for validator registration, should be integer greater than or equal to 100,000 MON"
            )
            return
    except Exception as e:
        log.error(f"Error during input validation: {e}")

    # Generate the pubkeys and address
    try:
        keygen = KeyGenerator.from_keys(
            secp_private_key=secp_privkey, bls_private_key=bls_privkey
        )
        secp_pubkey = keygen.pub_secp_key()
        bls_pubkey = keygen.pub_bls_key()
        log.info(f"SECP Pubkey: {secp_pubkey.hex()}")
        log.info(f"BLS Pubkey: {bls_pubkey.hex()}")
    except Exception as e:
        log.error(
            f"Key derivation failed: Your keys fall in the correct curve order but are incompatible with the cryptographic scheme: {e}"
        )
        return

    # from config
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    amount_wei = wei(amount)
    add_validator_call_data = add_validator(keygen, amount_wei, auth_address)
    log.debug(add_validator_call_data)

    is_confirmed = Confirm.ask(
        "[bold yellow]Do the derived public keys match? (make sure that the private keys were recovered using monad-keystore) [/]",
        default=False,  # Make the safe option the default
    )

    # Verify inputs and derivations
    if is_confirmed:
        pass
    else:
        return

    # send tx
    try:
        tx_hash = send_transaction(
            w3,
            signer,
            contract_address,
            add_validator_call_data,
            chain_id,
            amount_wei,
            gas_limit=2_000_000,
        )
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        log.error(f"Error while sending tx: {e}")
        return
    log.info(f"Tx status: {receipt.status}")
    log.info(f"Tx hash: 0x{receipt.transactionHash.hex()}")
    get_validator_registration_event(config, receipt)


def get_validator_registration_event(config, receipt):
    log = init_logging(config["log_level"].upper())
    abi = [
        {
            "name": "ValidatorCreated",
            "type": "event",
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "valId", "type": "uint64"},
                {"indexed": True, "name": "auth_delegator", "type": "address"},
                {"indexed": False, "name": "commission", "type": "uint256"},
            ],
        }
    ]

    rpc_url = config["rpc_url"]
    contract_address = config["contract_address"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not receipt:
        receipt = w3.eth.wait_for_transaction_receipt(
            "768f8911c7db93e5910c0f92d7cd71807a9b58d24de5e95deda8f219ca541e21"
        )
    with warnings.catch_warnings():
        # This tells the context to ignore UserWarnings where the message
        # starts with "The log with transaction hash".
        warnings.filterwarnings(
            "ignore",
            message="The log with transaction hash",
            category=UserWarning,
        )
        staking_contract = w3.eth.contract(address=contract_address, abi=abi)
        events = staking_contract.events.ValidatorCreated().process_receipt(receipt)
    if not events:
        log.error("No 'ValidatorCreated' event found in the transaction.")
        return
    for event in events:
        print()
        log.info(
            f"Validator Created! ID: {event['args']['valId']}, Delegator: {event['args']['auth_delegator']}, Commission: {event['args']['commission']}"
        )
