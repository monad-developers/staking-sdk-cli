from web3 import Web3
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from staking_sdk_py.generateCalldata import change_commission
from staking_sdk_py.signer_factory import Signer
from src.helpers import val_id_prompt, confirmation_prompt, send_transaction
from src.query import validator_exists, get_validator_info
from src.logger import init_logging

console = Console()


def change_validator_commission(config: dict, signer: Signer):
    colors = config["colors"]
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    auth_address = signer.get_address()

    # ===== COMMISSION PARAMETERS  =====
    validator_id = val_id_prompt(config)

    # Get current commission
    try:
        validator_info = get_validator_info(config, validator_id)
        # Commission is at index 4 in the validator info tuple
        current_commission_raw = validator_info[4]
        # Commission scale is 1e18, so divide by 1e16 to get percentage
        current_commission_percentage = current_commission_raw / (10**16)

        print("")

        console.print(
            Panel(
                f"""
        [{colors["secondary_text"]}]Validator ID: [{colors["highlight"]}]{validator_id}[/]
        [{colors["secondary_text"]}]Current Commission: [{colors["highlight"]}]{current_commission_percentage}%[/]
        """,
                title="[bold]Validator Information[/]",
                border_style=colors["border"],
            )
        )

    except Exception as e:
        console.print(f"[red]Warning: Could not retrieve current commission: {e}[/]")

    # Set new commission
    while True:
        try:
            commission_input = console.input(
                f"[{colors['primary_text']}]Enter new commission rate as percentage (0-100): [/]"
            )
            commission_percentage = float(commission_input)
            if commission_percentage == current_commission_percentage:
                console.print(
                    f"[yellow]New commission ({commission_percentage}) is the same as the current commission ({current_commission_percentage}). No change required.[/]"
                )
            elif 0 <= commission_percentage <= 100:
                # Convert percentage to 1e18 scale
                commission = int(commission_percentage * (10**16))
                break
            else:
                console.print(
                    f"[red]Commission must be between 0 and 100 (inclusive). You entered: {commission_percentage}[/]"
                )
        except ValueError:
            console.print(
                f"[red]Please enter a valid number. You entered: {commission_input}[/]"
            )

    print("")
    console.print(
        Panel(
            f"""
    [{colors["primary_text"]}]Validator ID: [{colors["highlight"]}]{validator_id}[/]
    Current Commission: [{colors["secondary_text"]}]{current_commission_percentage}%[/]
    New Commission: [{colors["highlight"]}]{commission_percentage}%[/]
    Auth Address: [{colors["secondary_text"]}] {auth_address}[/][/]
    """,
            title="[bold ]Change Commission[/]",
            border_style=colors["border"],
        )
    )

    confirmation = confirmation_prompt("Do you want to continue?", default=False)
    if confirmation:
        calldata_change_commission = change_commission(validator_id, commission)
        try:
            tx_hash = send_transaction(
                w3,
                signer,
                contract_address,
                calldata_change_commission,
                chain_id,
                0,
            )
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            console.print(f"Error! while trying to send tx: {e}")
            return

        print("")

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

        if receipt.status == 1:
            console.print(
                Panel(
                    f"[bold green]Commission successfully changed! ✅[/]\n\nValidator {validator_id} commission is now set to {commission_percentage}%",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]Transaction failed! ❌[/]\n\nCommission change was not successful for validator {validator_id}",
                    border_style="red",
                )
            )


def change_validator_commission_cli(
    config: dict, signer: Signer, val_id: int, commission_percentage: float
):
    log = init_logging(config["log_level"])

    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    # Validate input and get current commission
    try:
        val_info = get_validator_info(config, val_id)
        if not validator_exists(val_info):
            log.error("Invalid validator ID")
            return
        elif not (0 <= commission_percentage <= 100):
            log.error(
                f"Invalid commission rate: {commission_percentage}%. Must be between 0 and 100 (inclusive)"
            )
            return

        # Convert percentage to 1e18 scale
        commission = int(commission_percentage * (10**16))
        # Commission is at index 4 in the validator info tuple
        current_commission_raw = val_info[4]
        # Commission scale is 1e18, so divide by 1e16 to get percentage
        current_commission_percentage = current_commission_raw / (10**16)

        log.info(f"Validator ID: {val_id}")
        log.info(f"Current commission: {current_commission_percentage}%")
        log.info(f"New commission: {commission_percentage}%")

    except Exception as e:
        log.error(f"Error while validating inputs: {e}")
        return

    calldata_change_commission = change_commission(val_id, commission)

    # Set tx to set new commission
    try:
        tx_hash = send_transaction(
            w3,
            signer,
            contract_address,
            calldata_change_commission,
            chain_id,
            0,
        )
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        log.error(f"Error while trying to send tx: {e}")
        return

    log.info(f"Tx status: {receipt.status}")
    log.info(f"Tx hash: 0x{receipt.transactionHash.hex()}")

    if receipt.status == 1:
        log.info(
            f"Commission successfully changed from {current_commission_percentage}% to {commission_percentage}% for validator {val_id}"
        )
    else:
        log.error(
            f"Transaction failed! Commission change was not successful for validator {val_id}"
        )
