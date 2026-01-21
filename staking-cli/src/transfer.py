
from rich.console import Console
from rich.table import Table
from src.helpers import (
    address_prompt,
    amount_prompt,
    confirmation_prompt,
    send_transaction,
    wei,
)
from src.logger import init_logging
from web3 import Web3

from staking_sdk_py.signer_factory import Signer

console = Console()


def transfer(config: dict, signer: Signer):
    # read config
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    from_address = signer.get_address()

    # Parameters for transfer
    to_address = address_prompt(config, "recipient")
    transfer_amount = amount_prompt(config, description="to transfer")
    amount = wei(transfer_amount)

    # Check balance
    balance = w3.eth.get_balance(from_address)
    if balance < amount:
        console.print("[bold red]Insufficient balance![/]")
        return

    table = Table(
        show_header=False,
        title="Transfer Script Inputs",
        title_style="red bold",
        expand=True,
        show_lines=True,
    )
    table.add_column("Inputs")
    table.add_column("Values")
    table.add_row("[cyan][bold red]Recipient Address[/]:[/]", f"[green]{to_address}[/]")
    table.add_row(
        "[cyan][bold red]Amount to Transfer[/]:[/]",
        f"[green]{transfer_amount} MON ({amount} wei)[/]",
    )
    table.add_row("[cyan][bold red]From Address[/]:[/]", f"[green]{from_address}[/]")
    table.add_row("[cyan][bold red]RPC[/]:[/]", f"[green]{rpc_url}[/]")
    console.print(table)

    is_confirmed = confirmation_prompt(
        "Do the inputs above look correct?", default=False
    )

    if is_confirmed:
        # Generate transaction
        try:
            tx_hash = send_transaction(w3, signer, to_address, "0x", chain_id, amount)
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
        tx_table.add_row("To", receipt.to)
        console.print(tx_table)


def transfer_cli(config: dict, signer: Signer, args):
    log = init_logging(config["log_level"])
    # read config
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    from_address = signer.get_address()

    to_address = args.address
    amount_mon = args.amount
    force = args.force

    # Validate address
    if not Web3.is_address(to_address):
        log.error("Invalid recipient address")
        return
    to_address = Web3.to_checksum_address(to_address)

    # Get balance
    balance_wei = w3.eth.get_balance(from_address)

    amount_wei = wei(amount_mon)

    # Check sufficient balance
    if balance_wei < amount_wei:
        log.error(
            f"Insufficient balance. Have {balance_wei / 10**18:.2f} MON, need {amount_mon:.2f} MON"
        )
        return

    # Confirmation
    if not force:
        console = Console()
        table = Table(
            show_header=False,
            title="Transfer Details",
            expand=True,
        )
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Recipient Address", to_address)
        table.add_row("Amount", f"{amount_mon:.2f} MON ({amount_wei} wei)")
        table.add_row("From Address", from_address)
        console.print(table)
        is_confirmed = confirmation_prompt("Confirm transfer?", default=False)
        if not is_confirmed:
            log.info("Transfer cancelled")
            return

    # Send transaction
    try:
        tx_hash = send_transaction(w3, signer, to_address, "0x", chain_id, amount_wei)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        log.error(f"Error while sending tx: {e}")
        return

    log.info(f"Tx hash: 0x{receipt.transactionHash.hex()}")
