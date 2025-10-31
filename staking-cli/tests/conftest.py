import sys
from pathlib import Path

# Add the staking-cli directory to the Python path
staking_cli_dir = Path(__file__).parent.parent
sys.path.insert(0, str(staking_cli_dir))

