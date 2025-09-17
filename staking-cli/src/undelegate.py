from web3 import Web3
from staking_sdk_py.generateCalldata import undelegate
from staking_sdk_py.generateTransaction import send_transaction
from staking_sdk_py.callGetters import call_getter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.helpers import number_prompt, val_id_prompt, amount_prompt, wei, count_zeros, confirmation_prompt
from src.logger import init_logging

console = Console()

def undelegate_from_validator(config: dict):
    log = init_logging(config["log_level"])
    # read config
    contract_address = config["contract_address"]
    funded_private_key = config["staking"]["funded_address_private_key"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    # ===== UNDELEGATION PARAMETERS  =====
    delegation_amount = amount_prompt(config, description="to undelegate from validator")
    amount = wei(delegation_amount)
    validator_id = str(val_id_prompt(config))
    withdrawal_id = int(number_prompt("Enter Withdrawal ID", default="33"))

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    delegator_address = w3.eth.account.from_key(funded_private_key).address

    table = Table(show_header=False,
        title="Undelegate Script Inputs",
        title_style="red bold",
        expand=True,
        show_lines=True,
    )
    table.add_column("Inputs")
    table.add_column("Values")
    table.add_row("[cyan][bold red]Validator ID[/] to undelegate from:[/]", f"[green]{validator_id}[/]")
    table.add_row("[cyan][bold red]Amount[/] to undelegate:[/]", f"[green]{delegation_amount} MON ({amount} wei (contains {count_zeros(amount)} zeros))[/]")
    table.add_row("[cyan][bold red]Withdrawal ID[/] for this request:[/]", f"[green]{withdrawal_id}[/]")
    table.add_row("[cyan][bold red]Funded Address:[/]", f"[green]{delegator_address}[/]")
    table.add_row("[cyan][bold red]RPC[/] to use for tx:[/]", f"[green]{rpc_url}[/]")
    table.add_row("[cyan][bold red]Staking Contract Address[/] for the network:[/]", f"[green]{contract_address}[/]")
    console.print(table)

    is_confirmed = confirmation_prompt("Do the inputs above look correct?", default=False)

    if is_confirmed:
        # PREFLIGHT CHECKS
        console.print(Panel("[bold yellow]Running Preflight Checks...[/]", title="[bold red]Preflight[/]", border_style="yellow"))
        # 1. Check if withdrawal request already exists
        try:
            withdrawal_request = call_getter(w3, 'get_withdrawal_request', contract_address, validator_id, delegator_address, withdrawal_id)
            log.debug(f"Existing withdrawal request check: {withdrawal_request}")
            if withdrawal_request and withdrawal_request[0] > 0:
                log.error("Withdrawal request already exists for this ID!")
                return
            else:
                log.debug("✅ No existing withdrawal request - can proceed")
        except Exception as e:
            log.error(f"Encountered error while checking withdrawals: {e}")
            return

    # 2. Check delegator balance
        try:
            delegator_info = call_getter(w3, 'get_delegator', contract_address, int(validator_id), delegator_address)
            current_stake = delegator_info[0] if delegator_info else 0  # activeStake field
            if current_stake < amount:
                log.error(f"Insufficient stake! Current: {current_stake}, Requested: {amount}")
                console.print(f"Delegator Info: {delegator_info}")
                return
            else:
                log.debug(f"✅ Sufficient stake available: {current_stake}")
        except Exception as e:
            log.error(f"Error checking delegator info: {e}")
            return

        preflight_panel = Panel(
            '''
            [cyan]Withdrawal request status:[/] [green]Clear ✅[/]
            [cyan]Delegator stake balance:[/] [green]Sufficient ✅[/]
            [cyan]Ready to proceed with undelegation[/]
            ''',
            title="[bold green]Preflight Results[/]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(preflight_panel)


        # Generate calldata and send transaction
        calldata_undelegate = undelegate(int(validator_id), amount, withdrawal_id)
        if config["log_level"] == "debug":
            console.print(f"\n\n[cyan]Generated calldata:[/] [green]{calldata_undelegate}[/]")

        try:
            tx_hash = send_transaction(w3, funded_private_key, contract_address, calldata_undelegate, chain_id, 0)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
           console.print(f"Error! while sending tx: {e}")
           return

        if config["log_level"] == "debug":
            console.print(f'\n\n[bold green]Transaction receipt:[/] {receipt}')

        # Check withdrawal request was created
        withdrawal_request_after = call_getter(w3, 'get_withdrawal_request', contract_address, validator_id, delegator_address, withdrawal_id)

        validation_panel = Panel(
            f'''
            [cyan]Withdrawal request amount:[/] [green]{withdrawal_request_after[0] if withdrawal_request_after else 0}[/]
            [cyan]Withdrawal epoch:[/] [green]{withdrawal_request_after[2] if withdrawal_request_after else 0}[/]
            ''',
            title="[bold green]Undelegation Complete[/]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(validation_panel)

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

def undelegate_from_validator_cli(config: dict, val_id: int, amount: int, withdrawal_id: int):
    log = init_logging(config["log_level"])
    contract_address = config["contract_address"]
    funded_private_key = config["staking"]["funded_address_private_key"]
    rpc_url = config["rpc_url"]
    chain_id = config["chain_id"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    delegator_address = w3.eth.account.from_key(funded_private_key).address

    # check withdrawal id is usable
    try:
        withdrawal_request = call_getter(w3, 'get_withdrawal_request', contract_address, val_id, delegator_address, withdrawal_id)
        log.debug(f"Existing withdrawal request check: {withdrawal_request}")
        if withdrawal_request and withdrawal_request[0] > 0:
            log.error("Withdrawal request already exists for this ID!")
            return
        else:
            log.debug("✅ No existing withdrawal request - can proceed")
    except Exception as e:
        log.error(f"Encountered error while checking withdrawals: {e}")
        return

    # check if stake is greater than undelegate amount
    try:
        delegator_info = call_getter(w3, 'get_delegator', contract_address, int(val_id), delegator_address)
        current_stake = delegator_info[0] if delegator_info else 0  # activeStake field
        if current_stake < amount:
            log.error(f"Insufficient stake! Current: {current_stake}, Requested: {amount}")
            log.error(f"Delegator Info: {delegator_info}")
            return
        else:
            log.debug(f"✅ Sufficient stake available: {current_stake}")
    except Exception as e:
        log.error(f"Error checking delegator info: {e}")
        return

    amount = wei(amount)
    calldata_undelegate = undelegate(int(val_id), amount, withdrawal_id)
    log.debug(calldata_undelegate)

    # send tx
    try:
        tx_hash = send_transaction(w3, funded_private_key, contract_address, calldata_undelegate, chain_id, 0)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        log.error(f"Error while sending tx: {e}")
        return
    log.info(f"Tx status: {receipt.status}")
    log.info(f"Tx hash: {receipt.transactionHash.hex()}")
