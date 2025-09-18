import os
import sys
import toml
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from src.logger import init_logging
from src.add_validator import register_validator, register_validator_cli
from src.delegate import delegate_to_validator, delegate_to_validator_cli
from src.undelegate import undelegate_from_validator, undelegate_from_validator_cli
from src.withdraw import withdraw_delegation, withdraw_delegation_cli
from src.claim import claim_pending_rewards, claim_pending_rewards_cli
from src.compound import compound_rewards, compound_rewards_cli
from src.change_commission import change_validator_commission, change_validator_commission_cli
from src.query_menu import query, query_cli
from src.parser import init_parser
from src.helpers import number_prompt, confirmation_prompt

class StakingCLI:
    def __init__(self):
        self.console = Console()
        # argument parsing
        parser = init_parser()
        try:
           self.args = parser.parse_args()
        except argparse.ArgumentError as e:
            print(f"Error while trying to parse arguments: {e}")
            sys.exit()
        # validation
        if self.args.command == None:
            print("No command provided, exiting CLI. Try --help to understand various commands.")
            sys.exit()
        elif self.args.command == "query" and self.args.query == None:
           print("No sub-command provided for the query command. Try --help to understand various sub-commands.")
           sys.exit()
        # config and logging
        self.read_config(self.args.config_path)
        self.log = init_logging(self.config["log_level"].upper())
        self.colors = self.config["colors"]


    def read_config(self, config_path):
        '''Reads the toml config file'''
        # Verify config file
        if os.path.isfile(config_path):
            pass
        else:
            self.console.print(f"The provided config path: {config_path} is not a file.")
            sys.exit()

        # Read config file
        try:
            with open(config_path, "r") as f:
                self.config = toml.load(f)
        except toml.TomlDecodeError as e:
            print(f"Error decoding TOML file: {e}")
            exit()

    def tui(self):
        menu_text = f'''
        [{self.colors["primary_text"]}]1. Add Validator[/]\n
        [{self.colors["primary_text"]}]2. Delegate[/]\n
        [{self.colors["primary_text"]}]3. Undelegate[/]\n
        [{self.colors["primary_text"]}]4. Withdraw[/]\n
        [{self.colors["primary_text"]}]5. Claim Rewards[/]\n
        [{self.colors["primary_text"]}]6. Compound[/]\n
        [{self.colors["primary_text"]}]7. Change Commission[/]\n
        [{self.colors["primary_text"]}]8. Query[/]\n
        [{self.colors["primary_text"]}]9. Exit[/]\n
        '''
        menu_text = Align(menu_text, align="left")
        main_panel = Panel(
            menu_text,
            title=f"[bold {self.colors["main"]}]Staking Cli Menu[/]",
            padding=(0, 10, 0, 0),
            expand=False
        )
        while True:
            choices = [str(x) for x in range(1,10)]
            self.console.print(main_panel)
            choice = number_prompt("Enter a number as a choice", choices, default="9")

            if choice == "1":
                register_validator(self.config)
                self.log.info("Exited Add Validator\n\n")
            elif choice == "2":
                delegate_to_validator(self.config)
                self.log.info("Exited Delegate\n\n")
            elif choice == "3":
                undelegate_from_validator(self.config)
                self.log.info("Exited Undelegate\n\n")
            elif choice == "4":
                withdraw_delegation(self.config)
                self.log.info("Exited Withdraw\n\n")
            elif choice == "5":
                claim_pending_rewards(self.config)
                self.log.info("Exited Claim Rewards\n\n")
            elif choice == "6":
                compound_rewards(self.config)
                self.log.info("Exited Compound Rewards\n\n")
            elif choice == "7":
                change_validator_commission(self.config)
                self.log.info("Exited Change Commission\n\n")
            elif choice == "8":
                query(self.config)
                self.log.info("Exited Query Menu\n\n")
            elif choice == "9":
                self.log.info("Staking CLI has been exited!")
                sys.exit()

            continue_cli = confirmation_prompt("Do you want to go back to Main Menu?", default=True)
            if  not continue_cli:
                self.log.info("\nStaking CLI has been exited!")
                break

    def main(self):
        if self.args.command == "tui":
            self.tui()
        elif self.args.command == "add-validator":
            secp_privkey = self.args.secp_privkey
            bls_privkey = self.args.bls_privkey
            auth_address = self.args.auth_address
            amount = self.args.amount
            register_validator_cli(self.config, secp_privkey, bls_privkey, auth_address, amount)
        elif self.args.command == "delegate":
            validator_id = self.args.validator_id
            amount = self.args.amount
            delegate_to_validator_cli(self.config, validator_id, amount)
        elif self.args.command == "undelegate":
            validator_id = self.args.validator_id
            withdrawal_id = self.args.withdrawal_id
            amount = self.args.amount
            undelegate_from_validator_cli(self.config, validator_id, amount, withdrawal_id)
        elif self.args.command == "withdraw":
            validator_id = self.args.validator_id
            withdrawal_id = self.args.withdrawal_id
            withdraw_delegation_cli(self.config, validator_id, withdrawal_id)
        elif self.args.command == "claim-rewards":
            validator_id = self.args.validator_id
            claim_pending_rewards_cli(self.config, validator_id)
        elif self.args.command == "compound-rewards":
            validator_id = self.args.validator_id
            compound_rewards_cli(self.config, validator_id)
        elif self.args.command == "change-commission":
            validator_id = self.args.validator_id
            commission_percentage = self.args.commission
            change_validator_commission_cli(self.config, validator_id, commission_percentage)
        elif self.args.command == "query":
            query_cli(self.config, self.args)


if __name__ == "__main__":
    StakingCLI().main()
