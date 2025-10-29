from argparse import Namespace
from web3 import Web3
from staking_sdk_py.signer_factory import Signer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from src.helpers import (
    address_prompt,
    is_valid_address,
    number_prompt,
    confirmation_prompt,
    val_id_prompt,
)
from src.logger import init_logging
from src.query import (
    get_validator_info,
    get_validators_list,
    validator_exists,
    get_validator_set,
    get_delegator_info,
    get_withdrawal_info,
    get_delegators_list,
    get_tx_by_hash,
    get_epoch_info,
)

console = Console()


def print_query_menu(config):
    colors = config["colors"]
    """Prints the query menu"""
    menu_text = f"""
    [{colors["primary_text"]}]1. Validator Info[/]\n
    [{colors["primary_text"]}]2. Delegator Info[/]\n
    [{colors["primary_text"]}]3. Withdrawal Request[/]\n
    [{colors["primary_text"]}]4. Consensus Validator Set[/]\n
    [{colors["primary_text"]}]5. Execution Validator Set[/]\n
    [{colors["primary_text"]}]6. Snapshot Validator Set[/]\n
    [{colors["primary_text"]}]7. Delegators for a Validator[/]\n
    [{colors["primary_text"]}]8. Validators for a Delegator[/]\n
    [{colors["primary_text"]}]9. Epoch Info[/]\n
    [{colors["primary_text"]}]10. Exit[/]\n
    """
    menu_text = Align(menu_text, align="left")
    main_panel = Panel(
        menu_text,
        title=f"[bold {colors['main']}]Query Menu[/]",
        padding=(0, 10, 0, 0),
        expand=False,
    )
    choices = [str(x) for x in range(1, 11)]
    console.print(main_panel)
    choice = number_prompt("Enter a number as a choice", choices, default="10")

    return choice


def print_validator(val_info, val_id, verbose):
    # print in validator info in table
    val_fields = [
        ("AuthAddress", ""),
        ("flags", ""),
        ("Execution View: Stake", "wei"),
        ("Accumulated rewards per token", "wei"),
        ("Execution View: Commission", "%"),
        ("Unclaimed Rewards", "wei"),
        ("Consensus View: Stake", "wei"),
        ("Consensus View: Commission", "%"),
        ("Snapshot View: Stake", "wei"),
        ("Snapshot View: Commission", "%"),
        ("secp Pubkey", ""),
        ("bls Pubkey", ""),
    ]

    table = Table(title=f"Validator Info of: [red]val-id {val_id}[/]")
    table.add_column("Field", style="yellow")
    table.add_column("Value", style="cyan")
    console = Console()
    if verbose:
        for i in range(0, len(val_info)):
            # print(val_info[i]) # for debugging
            if type(val_info[i]) != bytes:
                if val_fields[i][0] == "flags":
                    pass
                elif val_fields[i][0] == "Accumulated rewards per token":
                    table.add_row(
                        val_fields[i][0],
                        str(val_info[i] / 10**36) + f" {val_fields[i][1]}",
                    )
                elif "Commission" in val_fields[i][0] and val_fields[i][1] == "%":
                    commission_percentage = val_info[i] / (10**16)
                    table.add_row(
                        val_fields[i][0],
                        f"{commission_percentage:.2f} {val_fields[i][1]}",
                    )
                else:
                    table.add_row(
                        val_fields[i][0], str(val_info[i]) + f" {val_fields[i][1]}"
                    )
            else:
                table.add_row(
                    val_fields[i][0], str(val_info[i].hex()) + f" {val_fields[i][1]}"
                )
        console.print(table)
    else:
        console.print(
            f"[cyan bold]{val_id}:[/cyan bold] [red]{val_info[10].hex()}[/red]"
        )


def print_validator_set(config, validator_set, verbose):
    for id in validator_set:
        val_info = get_validator_info(config, id)
        print_validator(val_info, id, verbose)


def print_delegator_info(delegator_info):
    table = Table(title="Delegator Status", show_header=False, expand=True)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    delegator_fields = [
        ("Stake", "wei"),
        ("Accumulated rewards per token", "wei"),
        ("Total Rewards", "wei"),
        ("Delta Stake", "wei"),
        ("Next Delta Stake", "wei"),
        ("Delta Epoch", ""),
        ("Next Delta Epoch", ""),
    ]

    for i in range(0, len(delegator_info)):
        # print(delegator_info[i]) # for debugging
        if type(delegator_info[i]) != bytes:
            if delegator_fields[i][0] == "Accumulated rewards per token":
                table.add_row(
                    delegator_fields[i][0],
                    str(delegator_info[i] / 10**36) + f" {delegator_fields[i][1]}",
                )
            else:
                table.add_row(
                    delegator_fields[i][0],
                    str(delegator_info[i]) + f" {delegator_fields[i][1]}",
                )
        else:
            table.add_row(
                delegator_fields[i][0],
                str(delegator_info[i].hex()) + f" {delegator_fields[i][1]}",
            )

    console.print(table)


def print_withdrawal_info(withdrawal_info):
    if not withdrawal_info or withdrawal_info[0] == 0:
        console.print("[bold red]❌ No withdrawal request found for this ID![/]")
        console.print(
            "[yellow]💡 You need to call undelegate first to create a withdrawal request or wait for 2 epochs after undelegation.[/]"
        )
        return

    withdrawal_amount = withdrawal_info[0]
    withdrawal_epoch = withdrawal_info[2]
    console.print(
        f"[bold green]✅ Withdrawal request found - Amount: {withdrawal_amount}, Epoch: {withdrawal_epoch}[/]"
    )


def print_delegators(delegators, val_id):
    console = Console()
    table = Table()
    table.add_column(f"Delegators for [red bold]val-id: {val_id}[/]")
    for delegator in delegators[2]:
        table.add_row(delegator, style="cyan")
    console.print(table)


def print_epoch(epoch_info):
    console = Console()
    table = Table()
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Epoch", str(epoch_info[0]))
    table.add_row("In Epoch Delay Period", str(epoch_info[1]))
    console.print(table)


def query(config: dict, signer: Signer):
    log = init_logging(config["log_level"])
    colors = config["colors"]
    while True:
        choice = print_query_menu(config)
        if choice == "1":
            validator_id = val_id_prompt(config)
            validator_info = get_validator_info(config, validator_id)
            # verbose = confirmation_prompt(f"[{colors["secondary_text"]}]Validator exists! Do you want a verbose output?[/]", default=False)
            print_validator(validator_info, validator_id, True)
        elif choice == "2":
            w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
            delegator_address = signer.get_address()
            address = address_prompt(
                config, "Enter delegator address:", default=delegator_address
            )
            validator_id = val_id_prompt(config)
            delegator_info = get_delegator_info(config, validator_id, address)
            print_delegator_info(delegator_info)
        elif choice == "3":
            w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
            delegator_address = signer.get_address()
            address = address_prompt(
                config, "Enter delegator address:", default=delegator_address
            )
            validator_id = val_id_prompt(config)
            withdrawal_id = int(number_prompt("Enter Withdrawal ID", default="33"))
            withdrawal_info = get_withdrawal_info(
                config, str(validator_id), address, withdrawal_id
            )
            print_withdrawal_info(withdrawal_info)
        elif choice == "4":
            validator_set = get_validator_set(config)
            verbose = confirmation_prompt(
                f"[{colors['secondary_text']}]Do you want a verbose output?[/]",
                default=False,
            )
            print_validator_set(config, validator_set, verbose)
        elif choice == "5":
            validator_set = get_validator_set(config, type="execution")
            verbose = confirmation_prompt(
                f"[{colors['secondary_text']}]Do you want a verbose output?[/]",
                default=False,
            )
            print_validator_set(config, validator_set, verbose)
        elif choice == "6":
            validator_set = get_validator_set(config, type="snapshot")
            verbose = confirmation_prompt(
                f"[{colors['secondary_text']}]Do you want a verbose output?[/]",
                default=False,
            )
            print_validator_set(config, validator_set, verbose)
        elif choice == "7":
            validator_id = val_id_prompt(config)
            delegators_list = get_delegators_list(config, validator_id)
            print_delegators(delegators_list, validator_id)
        elif choice == "8":
            w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
            delegator_address = signer.get_address()
            address = address_prompt(
                config, "Enter delegator address:", default=delegator_address
            )
            validator_list = get_validators_list(config, address)
            print_validator_set(config, validator_list[2], False)
        elif choice == "9":
            epoch_info = get_epoch_info(config)
            print_epoch(epoch_info)
        elif choice == "10":
            break

        continue_cli = confirmation_prompt("Continue Querying?", default=True)
        if not continue_cli:
            break


def query_cli(config: dict, args: Namespace):
    log = init_logging(config["log_level"])
    if args.query == "validator":
        validator_id = args.validator_id
        validator_info = get_validator_info(config, validator_id)
        if validator_exists(validator_info):
            print_validator(validator_info, validator_id, True)
        else:
            log.error("Error! Invalid Validator ID")
            return
    elif args.query == "delegator":
        w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
        delegator_address = args.delegator_address
        validator_id = args.validator_id
        validator_info = get_validator_info(config, validator_id)
        if validator_exists(validator_info):
            delegator_info = get_delegator_info(config, validator_id, delegator_address)
            print_delegator_info(delegator_info)
        else:
            log.error("Error! Invalid Validator ID")
            return
    elif args.query == "withdrawal-request":
        validator_id = args.validator_id
        address = args.delegator_address
        withdrawal_id = args.withdrawal_id
        validator_info = get_validator_info(config, validator_id)
        if not validator_exists(validator_info):
            log.error("Error! Invalid Validator ID")
            return
        if not is_valid_address(address):
            log.error("Error! Invalid Delegator Address")
            return
        withdrawal_info = get_withdrawal_info(
            config, str(validator_id), address, withdrawal_id
        )
        print_withdrawal_info(withdrawal_info)

    elif args.query == "validator-set":
        set_type = args.type
        if set_type not in ("consensus", "execution", "snapshot"):
            log.error(
                "Error! Invalid type, choose from: consensus, execution or snapshot"
            )
            return
        validator_set = get_validator_set(config, type=set_type)
        print_validator_set(config, validator_set, False)
    elif args.query == "delegators":
        validator_id = args.validator_id
        validator_info = get_validator_info(config, validator_id)
        if validator_exists(validator_info):
            validator_info = get_validator_info(config, validator_id)
        else:
            log.error("Error! Invalid Validator ID")
            return
        delegators_list = get_delegators_list(config, validator_id)
        print_delegators(delegators_list, validator_id)
    elif args.query == "delegations":
        address = args.delegator_address
        if not is_valid_address(address):
            log.error("Error! Invalid Delegator Address")
            return
        validator_list = get_validators_list(config, address)
        print_validator_set(config, validator_list[2], False)
    elif args.query == "epoch":
        epoch_info = get_epoch_info(config)
        print_epoch(epoch_info)
