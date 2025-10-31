from web3 import Web3
from staking_sdk_py.generateCalldata import withdraw
from staking_sdk_py.callGetters import call_getter
from staking_sdk_py.signer_factory import Signer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.helpers import number_prompt, confirmation_prompt, val_id_prompt, send_transaction
from src.logger import init_logging

console = Console()

# Number of epochs to wait before unstaked tokens can be withdrawn	
WITHDRAWAL_DELAY = 1

def withdraw_delegation(config: dict, signer: Signer):
    # read config
    colors = config["colors"]
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    # Parameters for withdrawal
    validator_id = val_id_prompt(config)
    withdrawal_id = int(number_prompt("Enter the Withdrawal ID"))

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    delegator_address = signer.get_address()

    table = Table(show_header=False,
        title="Withdraw Script Inputs",
        title_style="red bold",
        expand=True,
        show_lines=True,
    )
    table.add_column("Inputs")
    table.add_column("Values")
    table.add_row("[cyan][bold red]Validator ID[/] to withdraw from:[/]", f"[green]{validator_id}[/]")
    table.add_row("[cyan][bold red]Withdrawal ID[/] to process:[/]", f"[green]{withdrawal_id}[/]")
    table.add_row("[cyan][bold red]Funded Address to use for tx:[/]", f"[green]{delegator_address}[/]")
    table.add_row("[cyan][bold red]RPC[/] to use for tx:[/]", f"[green]{rpc_url}[/]")
    table.add_row("[cyan][bold red]Staking Contract Address[/] for the network:[/]", f"[green]{contract_address}[/]")
    console.print(table)

    is_confirmed = confirmation_prompt("Do the inputs above look correct?", default=False)

    if is_confirmed:

        # PREFLIGHT CHECKS
        console.print(Panel("[bold yellow]Running Preflight Checks...[/]", title="[bold red]Preflight[/]", border_style="yellow"))
        # 1. Check if withdrawal request exists and get withdrawal epoch
        try:
            withdrawal_request = call_getter(w3, 'get_withdrawal_request', contract_address, validator_id, delegator_address, withdrawal_id)
            if not withdrawal_request or withdrawal_request[0] == 0:
                console.print("[bold red]❌ No withdrawal request found for this ID![/]")
                console.print("[yellow]💡 You need to call undelegate first to create a withdrawal request or wait for 2 epochs after undelegation.[/]")
                return

            withdrawal_amount = withdrawal_request[0]
            withdrawal_epoch = withdrawal_request[2]
            console.print(f"[bold green]✅ Withdrawal request found - Amount: {withdrawal_amount}, Epoch: {withdrawal_epoch}[/]")
        except Exception as e:
            console.print(f"[bold red]❌ Error checking withdrawal request: {e}[/]")
            return

        # 2. Check current epoch vs withdrawal epoch
        try:
            epoch_info = call_getter(w3, 'get_epoch', contract_address)
            current_epoch = epoch_info[0] if epoch_info else 0
            withdrawal_allowed_epoch = withdrawal_epoch + WITHDRAWAL_DELAY
            console.print(f"[cyan]Current epoch:[/] [green]{current_epoch}[/]")
            console.print(f"[cyan]Required withdrawal epoch:[/] [green]{withdrawal_allowed_epoch}[/]")

            if current_epoch < withdrawal_allowed_epoch:
                console.print(f"[bold red]❌ Cannot withdraw yet! Current epoch: {current_epoch}, Need to wait until: {withdrawal_allowed_epoch}[/]")
                console.print(f"[yellow]💡 Please wait {withdrawal_allowed_epoch - current_epoch} more epoch(s)[/]")
                return
            else:
                console.print("[bold green]✅ Withdrawal epoch reached - can withdraw now[/]")

        except Exception as e:
            console.print(f"[bold red]❌ Error checking epoch: {e}[/]")
            return

        preflight_panel = Panel(
            f'''
            [cyan]Withdrawal request:[/] [green]Found ✅[/]
            [cyan]Withdrawal amount:[/] [green]{withdrawal_amount} wei[/]
            [cyan]Epoch check:[/] [green]Ready ✅[/]
            [cyan]Current epoch:[/] [green]{current_epoch}[/]
            [cyan]Required epoch:[/] [green]{withdrawal_allowed_epoch}[/]
            ''',
            title="[bold green]Preflight Results[/]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(preflight_panel)

        # Generate calldata and send transaction
        calldata_withdraw = withdraw(validator_id, withdrawal_id)
        try:
            tx_hash = send_transaction(w3, signer, contract_address, calldata_withdraw, chain_id, 0)
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

def withdraw_delegation_cli(config: dict, signer: Signer, val_id: int, withdrawal_id: int):
    log = init_logging(config["log_level"])
    # read config
    contract_address = config["contract_address"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    delegator_address = signer.get_address()

    # Check if withdrawal request is present
    try:
        withdrawal_request = call_getter(w3, 'get_withdrawal_request', contract_address, val_id, delegator_address, withdrawal_id)
        if not withdrawal_request or withdrawal_request[0] == 0:
            log.error("No withdrawal request found for this ID")
            return
        withdrawal_amount = withdrawal_request[0]
        withdrawal_epoch = withdrawal_request[2]
        log.info(f"Withdrawal request found - Amount: {withdrawal_amount}, Epoch: {withdrawal_epoch}")
    except Exception as e:
        log.error(f"[bold red]❌ Error checking withdrawal request: {e}")
        return

    # 2. Check current epoch vs withdrawal epoch
    try:
        epoch_info = call_getter(w3, 'get_epoch', contract_address)
        current_epoch = epoch_info[0] if epoch_info else 0
        withdrawal_allowed_epoch = withdrawal_epoch + WITHDRAWAL_DELAY
        log.info(f"Current epoch: {current_epoch}")
        log.info(f"Required withdrawal epoch: {withdrawal_allowed_epoch}")

        if current_epoch < withdrawal_allowed_epoch:
            log.error(f"Cannot withdraw yet! Current epoch: {current_epoch}, Need to wait until: {withdrawal_allowed_epoch}")
            log.error(f"Please wait {withdrawal_allowed_epoch - current_epoch} more epoch(s)")
            return
        else:
            log.info("✅ Withdrawal epoch reached - can withdraw now")
    except Exception as e:
        console.print(f"Error checking epoch: {e}")
        return

    calldata_withdraw = withdraw(val_id, withdrawal_id)

    # send tx
    try:
        tx_hash = send_transaction(w3, signer, contract_address, calldata_withdraw, chain_id, 0)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        log.error(f"Error while sending tx: {e}")
        return

    log.info(f"Tx status: {receipt.status}")
    log.info(f"Tx hash: 0x{receipt.transactionHash.hex()}")
