import web3
from web3 import Web3
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from staking_sdk_py.callGetters import call_getter
from staking_sdk_py.generateCalldata import delegate
from staking_sdk_py.generateTransaction import send_transaction
from src.helpers import wei, amount_prompt, val_id_prompt, confirmation_prompt, count_zeros, is_valid_amount
from src.query_menu import print_delegator_info
from src.query import validator_exists, get_validator_info
from src.logger import init_logging

console = Console()

def delegate_to_validator(config: dict):
    # read config
    colors = config["colors"]
    contract_address = config["contract_address"]
    funded_private_key = config["staking"]["funded_address_private_key"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    delegator_address = w3.eth.account.from_key(funded_private_key).address

    # ===== DELEGATION PARAMETERS  =====
    delegation_amount = amount_prompt(config, description="to delegate to validator")
    amount = wei(delegation_amount)
    validator_id = val_id_prompt(config)

    console.print(Panel(f'''
    [{colors["primary_text"]}]Delegating [{colors["highlight"]}]{delegation_amount} MON ({amount} wei (contains {count_zeros(amount)} zeros))[/]
    To: Validator [{colors["highlight"]}]{validator_id}[/]
    From Address: [{colors["secondary_text"]}] {delegator_address}[/][/]
    ''',
    title="[bold ]Delegate[/]",
    border_style=colors["border"]))

    confirmation = confirmation_prompt("Do you want to continue?", default=False)
    if confirmation:
        calldata_delegate = delegate(validator_id)
        try:
            tx_hash = send_transaction(w3, funded_private_key, contract_address, calldata_delegate, chain_id, amount)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            console.print(f"Error! while trying to send tx: {e}")
            return

        # Create formatted transaction summary
        tx_table = Table(title="Transaction Results", show_header=False, expand=True)
        tx_table.add_column("Field", style="cyan")
        tx_table.add_column("Value", style="green")
        tx_table.add_row("Status", "✅ Success" if receipt.status == 1 else "❌ Failed")
        tx_table.add_row("Transaction Hash", "0x"+receipt.transactionHash.hex())
        tx_table.add_row("Block Number", str(receipt.blockNumber))
        tx_table.add_row("Gas Used", f"{receipt.gasUsed:,}")
        tx_table.add_row("From", receipt['from'])
        tx_table.add_row("To (Contract)", receipt.to)
        console.print(tx_table)

        if receipt.logs:
            console.print(Panel("[bold yellow]Event Analysis[/]", border_style="yellow"))
            for log in receipt.logs:
                if len(log.topics) >= 3:
                    # This is likely a Delegate event
                    validator_id_from_log = int(log.topics[1].hex(), 16)
                    delegator_from_log = "0x" + log.topics[2].hex()[26:]  # Remove padding
                    # Parse data (amount and activation epoch)
                    data_hex = log.data.hex()
                    amount_from_log = int(data_hex[0:64], 16)
                    activation_epoch = int(data_hex[64:128], 16)
                    event_table = Table(title="Delegate Event", show_header=False, expand=True)
                    event_table.add_column("Field", style="cyan")
                    event_table.add_column("Value", style="green")
                    event_table.add_row("Event Type", "Delegate")
                    event_table.add_row("Validator ID", str(validator_id_from_log))
                    event_table.add_row("Delegator", delegator_from_log)
                    event_table.add_row("Amount", f"{amount_from_log} wei")
                    event_table.add_row("Activation Epoch", str(activation_epoch))
                    console.print(event_table)

                    # Get delegator info
                    console.print(Panel("[bold yellow]Delegator Information[/]", border_style="yellow"))
                    delegator_info = call_getter(w3,'get_delegator', contract_address, validator_id, delegator_address)

                    if delegator_info:
                        print_delegator_info(delegator_info)
                        console.print(Panel("[bold green]✅ Delegation Complete![/]", border_style="green"))

def delegate_to_validator_cli(config: dict, val_id: int, amount: int):
    log = init_logging(config["log_level"])
    # Input validation
    try:
        val_info = get_validator_info(config, val_id)
        if not validator_exists(val_info):
            log.error("Invalid validator id")
            return
        elif not is_valid_amount(amount, register=False):
            log.error("Invalid amount to delegate")
            return
    except Exception as e:
        log.error(f"Error while validating inputs: {e}")
        return

    # read config
    contract_address = config["contract_address"]
    funded_private_key = config["staking"]["funded_address_private_key"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    amount = wei(amount)
    calldata_delegate = delegate(val_id)
    log.debug(calldata_delegate)

    # send tx
    try:
        tx_hash = send_transaction(w3, funded_private_key, contract_address, calldata_delegate, chain_id, amount)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        log.error(f"Error! while trying to send tx: {e}")
        return
    log.info(f"Tx status: {receipt.status}")
    log.info(f"Tx hash: 0x{receipt.transactionHash.hex()}")
