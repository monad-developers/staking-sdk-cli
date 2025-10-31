# --- Constants ---
RPC_URL = ""
FUNDED_PRIVATE_KEY = ""
FUNDED_ADDRESS = ""
CONTRACTADDRESS = "0x0000000000000000000000000000000000001000"

# Write selectors
ADD_VALIDATOR_SELECTOR = "f145204c"
DELEGATE_SELECTOR = "84994fec"
UNDELEGATE_SELECTOR = "5cf41514"
COMPOUND_SELECTOR = "b34fea67"
WITHDRAW_SELECTOR = "aed2ee73"
CLAIM_REWARDS_SELECTOR = "a76e2ca5"
CHANGE_COMMISSION_SELECTOR = "9bdcc3c8"


# Read selectors
GET_EPOCH_SELECTOR = "757991a8"
GET_VALIDATOR_SELECTOR = "2b6d639a"
GET_DELEGATOR_SELECTOR = "573c1ce0"
GET_WITHDRAWAL_REQUEST_SELECTOR = "56fa2045"
GET_PROPOSER_VAL_ID = "fbacb0be"
GET_CONSENSUS_VALSET_SELECTOR = "fb29b729"
GET_SNAPSHOT_VALSET_SELECTOR = "de66a368"
GET_EXECUTION_VALSET_SELECTOR = "7cb074df"
GET_DELEGATIONS_SELECTOR = "4fd66050"
GET_DELEGATORS_SELECTOR = "a0843a26"




GETTER_ABIS = {
    "get_epoch": ["uint64", "bool"],
    "get_validator": ["address", "uint256", "uint256", "uint256", "uint256", "uint256", "uint256", "uint256","uint256", "uint256", "bytes", "bytes"],
    "get_delegator": ["uint256", "uint256", "uint256", "uint256", "uint256", "uint64", "uint64"],
    "get_withdrawal_request": ["uint256", "uint256", "uint64"],  
    "get_proposer_val_id": ["uint64"],
    "get_consensus_valset": ["bool", "uint64","uint64[]"],  
    "get_snapshot_valset": ["bool", "uint64","uint64[]"],   
    "get_execution_valset": ["bool", "uint64","uint64[]"],  
    "get_delegations": ["bool", "uint64", "uint64[]"],
    "get_delegators": ["bool", "address", "address[]"],
}

VALIDATOR_CREATED_EVENT_ABI = [
    "event ValidatorCreated(uint64 indexed valId, address indexed auth_delegator, uint256 commission)"
]

VALIDATOR_STATUS_CHANGED_EVENT_ABI = [
    "event ValidatorStatusChanged(uint64 indexed valId, uint64 flags)"
]

DELEGATE_EVENT_ABI = [
    "event Delegate(uint64 indexed valId, address indexed delegator, uint256 amount, uint64 activationEpoch)"
]

UNDELEGATE_EVENT_ABI = [
    "event Undelegate(uint64 indexed valId, address indexed delegator, uint8 withdrawal_id, uint256 amount, uint64 activationEpoch)"
]

WITHDRAWAL_EVENT_ABI = [
    "event Withdraw(uint64 indexed valId, address indexed delegator, uint8 withdrawal_id, uint256 amount, uint64 activationEpoch)"
]

CLAIM_REWARDS_EVENT_ABI = [
    "event ClaimRewards(uint64 indexed valId, address indexed delegator, uint256 amount, uint64 epoch)"
]
