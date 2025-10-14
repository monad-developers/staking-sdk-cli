import argparse


def init_parser() -> argparse.ArgumentParser:
    """Inits arg parser and makes sure config argument is passed"""
    parser = argparse.ArgumentParser(description="Staking CLI for Validators on Monad")

    # mandatory config path
    subparsers = parser.add_subparsers(dest="command")

    # sub-parsers
    add_validator_parser = subparsers.add_parser(
        "add-validator", help="Add a new validator to network"
    )
    delegate_parser = subparsers.add_parser(
        "delegate", help="Delegate to a validator in the network"
    )
    undelegate_parser = subparsers.add_parser(
        "undelegate", help="Undelegate Stake from validator"
    )
    withdraw_parser = subparsers.add_parser(
        "withdraw", help="Withdraw undelegated stake from validator"
    )
    claim_parser = subparsers.add_parser("claim-rewards", help="Claim staking rewards")
    compound_parser = subparsers.add_parser(
        "compound-rewards", help="Compound rewards to validator"
    )
    change_commission_parser = subparsers.add_parser(
        "change-commission", help="Change validator commission"
    )
    query_parser = subparsers.add_parser("query", help="Query network information")
    tui_parser = subparsers.add_parser("tui", help="Use a menu-driven TUI")

    # tui_parser
    tui_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # add_validator_parser
    add_validator_parser.add_argument(
        "--secp-privkey",
        type=str,
        required=True,
        help="secp privkey of validator to be added (id-secp)",
    )
    add_validator_parser.add_argument(
        "--bls-privkey",
        type=str,
        required=True,
        help="bls privkey of validator to be added (id-bls)",
    )
    add_validator_parser.add_argument(
        "--amount",
        type=int,
        required=True,
        help="Amount (in MON) to stake while adding validator (min: 100k  Mon)",
    )
    add_validator_parser.add_argument(
        "--auth-address",
        type=str,
        required=True,
        help="Authorised address to control validator operations",
    )
    add_validator_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # delegate_parser
    delegate_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    delegate_parser.add_argument(
        "--amount",
        type=int,
        required=True,
        help="Amount (in MON) to delegate to validator",
    )
    delegate_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # undelegate_parser
    undelegate_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    undelegate_parser.add_argument(
        "--amount",
        type=int,
        required=True,
        help="Amount (in MON) to undelegate to validator",
    )
    undelegate_parser.add_argument(
        "--withdrawal-id",
        type=int,
        required=True,
        help="Unique id to represent withdrawal request",
    )
    undelegate_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # withdraw_parser
    withdraw_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    withdraw_parser.add_argument(
        "--withdrawal-id",
        type=int,
        required=True,
        help="Unique id to represent withdrawal request",
    )
    withdraw_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # claim_parser
    claim_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    claim_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # compound_parser
    compound_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    compound_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # change_commission_parser
    change_commission_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    change_commission_parser.add_argument(
        "--commission",
        type=float,
        required=True,
        help="New commission rate as percentage (0.0 to 100.0)",
    )
    change_commission_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # query_parser
    query_subparser = query_parser.add_subparsers(dest="query")
    val_info_parser = query_subparser.add_parser(
        "validator", help="Show validator information"
    )
    delegator_info_parser = query_subparser.add_parser(
        "delegator", help="Show delegator information"
    )
    withdrawal_request_parser = query_subparser.add_parser(
        "withdrawal-request", help="Show withdrawal-request information"
    )
    validator_set_parser = query_subparser.add_parser(
        "validator-set", help="Show validator set"
    )
    delegators_parser = query_subparser.add_parser(
        "delegators", help="Show delegators for a validator"
    )
    delegations_parser = query_subparser.add_parser(
        "delegations", help="Show delegations done by an address"
    )
    epoch_parser = query_subparser.add_parser("epoch", help="Show epoch info")

    # val_info_parser
    val_info_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    val_info_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # delegator_info_parser
    delegator_info_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    delegator_info_parser.add_argument(
        "--delegator-address",
        type=str,
        required=True,
        help="Delegator address to query for",
    )
    delegator_info_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # withdrawal_request_parser
    withdrawal_request_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    withdrawal_request_parser.add_argument(
        "--withdrawal-id",
        type=int,
        required=True,
        help="Unique id to represent withdrawal request",
    )
    withdrawal_request_parser.add_argument(
        "--delegator-address",
        type=str,
        required=True,
        help="Delegator address to query for",
    )
    withdrawal_request_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # validator_set_parser
    validator_set_parser.add_argument(
        "--type",
        type=str,
        required=False,
        help="Type of set to show: consensus, execution or snapshot",
    )
    validator_set_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # delegators_parser
    delegators_parser.add_argument(
        "--validator-id",
        type=int,
        required=True,
        help="Unique id representing the validator on-chain",
    )
    delegators_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # delegations_parser
    delegations_parser.add_argument(
        "--delegator-address",
        type=str,
        required=True,
        help="Delegator address to query for",
    )
    delegations_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    # epoch_parser
    epoch_parser.add_argument(
        "--config-path",
        type=str,
        default="./config.toml",
        help="Add a path to a config.toml file",
    )

    return parser
