# Command Reference

### Add Validator

Register a new validator on the network.

**Requirements:**

- Minimum stake to join register validator: 100,000 MON
- Valid SECP256k1 private key (64 hex chars, **WITHOUT** 0x prefix)
- Valid BLS private key (64 hex chars, **WITH** 0x prefix)
- Make sure the `auth-address` is an address you control and intend to perform validator operations with. This can be the same as the funded address. You can provide another address here to decouple staking and operations.

```sh
python main.py add-validator \
--secp-privkey "{{ VALIDATOR PRIVATE SECP KEY }}" \
--bls-privkey "{{ VALIDATOR PRIVATE BLS KEY }}" \
--auth-address "{{ AN ADDRESS THAT YOU CONTROL }}" \
--amount 100000 \
--config-path ~/config.toml
```

**Expected Output:**

```sh
INFO     SECP Pubkey: 02a1b2c3d4e5f6789...
INFO     BLS Pubkey: b1a2b3c4d5e6f789...
INFO     Tx status: 1
INFO     Tx hash: 0x1234567890abcdef...
```

### Delegate

Delegate MON tokens to a validator.

```sh
python main.py delegate \
--validator-id 1 \
--amount 1000 \
--config-path ~/config.toml
```

**Expected Output:**

```sh
INFO     Tx status: 1
INFO     Tx hash: 0xabcdef1234567890...
```

### Undelegate

Create a withdrawal request to undelegate tokens.

```sh
python main.py undelegate \
--validator-id 1 \
--withdrawal-id 0 \
--amount 500 \
--config-path ~/config.toml
```

### Withdraw

Withdraw tokens from a completed undelegation request.

```sh
python main.py withdraw \
--validator-id 1 \
--withdrawal-id 0 \
--config-path ~/config.toml
```

**Note:** Withdrawals can only be processed after the required waiting period (typically 2 epochs).

### Claim Rewards

Claim accumulated staking rewards.

```sh
python main.py claim-rewards \
--validator-id 1 \
--config-path ~/config.toml
```

### Compound Rewards

Automatically restake rewards as additional delegation.

```sh
python main.py compound-rewards \
--validator-id 1 \
--config-path ~/config.toml
```

### Change Commission

Update the commission for a Validator. Commission is specified as percentage (0.0 to 100.0).

```sh
python main.py change-commission \
--validator-id 1 \
--commission 5.0 \
--config-path ~/config.toml
```

**Expected Output:**

```sh
INFO     Validator ID: 1
INFO     Current commission: 10.0%
INFO     New commission: 5.0%
INFO     Tx status: 1
INFO     Tx hash: 0xabcdef1234567890...
INFO     Commission successfully changed from 10.0% to 5.0% for validator 1
```

**Note:** Only the Validator's authorized address can change the commission.

## Query Commands

### Query Validator Information

```sh
python main.py query validator --validator-id 1 --config-path ~/config.toml
```

### Query Delegator Information

```sh
python main.py query delegator \
--validator-id 1 \
--delegator-address 0x742d35C... \
--config-path ~/config.toml
```

### Query Withdrawal Request

```sh
python main.py query withdrawal-request \
--validator-id 1 \
--delegator-address 0x742d35C... \
--withdrawal-id 0 \
--config-path ~/config.toml
```

### Query Validator Set

```sh
# Options: consensus, execution, snapshot
python main.py query validator-set --type consensus --config-path ~/config.toml
```

### Query Delegators for a Validator

```sh
python main.py query delegators --validator-id 1 --config-path ~/config.toml
```

### Query Validators for a Delegator

```sh
python main.py query delegations \
--delegator-address 0x742d35C... \
--config-path ~/config.toml
```

### Query Epoch Information

```sh
python main.py query epoch --config-path ~/config.toml
```

### Get Help for Any Command

```sh
python main.py add-validator --help
python main.py delegate --help
# etc.
```
