# staking-cli

A CLI tool to interact with Monad's staking contract and execute operations by interacting with it.

## Features

- Adding/Registering a Validator
- Delegating stake to a Validator
- Undelegating stake from a Validator
- Withdrawing pending undelegations using withdrawal IDs
- Claiming rewards
- Compounding rewards
- Changing Validator commission
- Querying staking state on the chain

## Security Notes

- **Please use hardware wallet for production environment**
  - Ledger wallets are [supported](https://github.com/mikeshultz/ledger-eth-lib?tab=readme-ov-file#ledger-devices) and tested with `Ledger Nano S Plus`
- Never commit your private key to version control
- Keep your config.toml file secure and private
- Use a funded address with sufficient balance for gas fees

## Prerequisites

- Python 3.8 or higher
- Git
- Access to a Monad RPC endpoint
- Private key with sufficient funds for transactions

## Installation

1. Clone the Repository

```sh
git clone https://github.com/monad-developers/staking-sdk-cli.git
cd staking-sdk-cli
```

2. Create a virtual environment and activate it

```sh
python -m venv cli-venv
source cli-venv/bin/activate  # On Windows: cli-venv\Scripts\activate
```

3. Install project dependencies

```sh
pip install .
```

To make changes to SDK code and have it reflected, use the `pip install -e .`.

## Upgrade

1. Fetch the latest commit on `main` branch

```sh
cd staking-sdk-cli
git checkout main
git pull
```

2. Activate the virtual environment

```sh
source cli-venv/bin/activate  # On Windows: cli-venv\Scripts\activate
```

3. Install project dependencies

```sh
pip install .
```

## Build an executable (optional)

1. Make sure you are in a virtual environment with all dependencies installed as given in steps above to make a build successfully.

```sh
source cli-venv/bin/activate  # On Windows: cli-venv\Scripts\activate
pip install pyinstaller
```

2. Run the pyinstaller command to create a spec

```sh
cd staking-cli
pyinstaller --additional-hooks-dir=./hooks --name monad-staking-cli --onedir --clean --noconfirm main.py
```

3. Create an executable

```sh
pyinstaller --noconfirm monad-staking-cli.spec
```

4. Execute the binary

```sh
./dist/monad-staking-cli/monad-staking-cli --help
```

The folder `dist/monad-staking-cli` can be archived and distributed.

## Configuration

The default config path is `config.toml`

1. Create and edit the configuration file

```sh
cp staking-cli/config.toml.example config.toml
```

## Usage

The stakin-cli tool supports two modes: `CLI` and `TUI`.

### CLI Mode

```sh
$ source cli-venv/bin/activate
$ python staking-cli/main.py --help

usage: main.py [-h]
               {add-validator,delegate,undelegate,withdraw,claim-rewards,compound-rewards,change-commission,query,tui} ...

Staking CLI for Validators on Monad

positional arguments:
  {add-validator,delegate,undelegate,withdraw,claim-rewards,compound-rewards,change-commission,query,tui}
    add-validator       Add a new validator to network
    delegate            Delegate to a validator in the network
    undelegate          Undelegate Stake from validator
    withdraw            Withdraw undelegated stake from validator
    claim-rewards       Claim staking rewards
    compound-rewards    Compound rewards to validator
    change-commission   Change validator commission
    query               Query network information
    tui                 Use a menu-driven TUI

options:
  -h, --help            show this help message and exit
```

### TUI Mode

Interactive Terminal User Interface mode for easier navigation.

```sh
$ source cli-venv/bin/activate
$ python staking-cli/main.py tui
╭────────── Staking Cli Menu ──────────╮
│                                      │
│        1. Add Validator              │
│                                      │
│        2. Delegate                   │
│                                      │
│        3. Undelegate                 │
│                                      │
│        4. Withdraw                   │
│                                      │
│        5. Claim Rewards              │
│                                      │
│        6. Compound                   │
│                                      │
│        7. Change Commission          │
│                                      │
│        8. Query                      │
│                                      │
│        9. Exit                       │
│                                      │
│                                      │
╰──────────────────────────────────────╯
```

## Documentations

- See the [Validator Onboarding](docs/validator-onboarding.md) for registering a new validator.
- See the [Command Reference](docs/command-reference.md) for more details.

### Example Workflow

1. **Setup**: Create `config.toml` with your details
2. **Query**: Check current validator set and epoch
3. **Delegate**: Start with a small delegation to test
4. **Monitor**: Query your delegation status
5. **Manage**: Claim rewards, compound, or undelegate as needed

## Important Notes

### Amount Units

- All amounts are specified in **MON units** (not wei)
- Example: `--amount 1000` = 1,000 MON tokens
- The CLI automatically converts MON to wei for blockchain transactions

### Key Formats

- **SECP Private Key**: 64 hexadecimal characters, **without `0x` prefix**
  - Example: `a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef`
- **BLS Private Key**: 64 hexadecimal characters, **with `0x` prefix**
  - Example: `0x1a2b3c4d5e6f7890123456789abcdef0123456789abcdef0123456789abcdef`

### Gas Requirements

- Validator registration: ~2M gas
- Delegation operations: ~1M gas
- The CLI automatically sets appropriate gas limits

## Troubleshooting

### Transaction Failures

If transactions fail with status `0`:

1. **Check gas limits**: Validator registration requires higher gas
2. **Verify amounts**: Ensure minimum requirements are met
3. **Check network**: Confirm RPC endpoint is accessible
4. **Validate keys**: Ensure proper key formats

### Common Errors

- **"Invalid Validator ID"**: Use `query validator-set` to see available validators
- **"Cannot withdraw yet"**: Wait for the required epoch delay
- **"Insufficient funds"**: Ensure your address has enough MON for the operation
- **"Key validation failed"**: Check key format and length

### Network Issues

- Verify your RPC URL is correct and accessible
- Check if the network is experiencing downtime
- Ensure your internet connection is stable
