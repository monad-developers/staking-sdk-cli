"""CLI entry point for staking-sdk-cli."""
import sys
import os
from pathlib import Path

def find_cli_directory():
    """Find the staking-cli directory in various possible locations."""
    # Try 1: Relative to this file (development)
    package_dir = Path(__file__).parent.parent.parent
    cli_dir = package_dir / 'staking-cli'
    if cli_dir.exists():
        return cli_dir

    # Try 2: In the installed package location
    try:
        import staking_sdk_py
        package_location = Path(staking_sdk_py.__file__).parent.parent
        cli_dir = package_location / 'staking-cli'
        if cli_dir.exists():
            return cli_dir
    except Exception:
        pass

    # Try 3: In share/staking-cli (if installed via shared-data)
    # pipx installs packages in ~/.local/pipx/venvs/<package>/share/<package>/
    try:
        import site
        import sysconfig
        # Try to find share directory in various locations
        for path in site.getsitepackages() + [sysconfig.get_path('data')]:
            share_dir = Path(path).parent / 'share' / 'staking-cli'
            if share_dir.exists():
                return share_dir
        # Also try relative to package
        import staking_sdk_py
        package_location = Path(staking_sdk_py.__file__).parent.parent
        share_dir = package_location.parent / 'share' / 'staking-cli'
        if share_dir.exists():
            return share_dir
    except Exception:
        pass

    # Try 4: Current directory (for development)
    cwd_cli = Path.cwd() / 'staking-cli'
    if cwd_cli.exists():
        return cwd_cli

    raise ImportError(
        f"Could not find staking-cli directory. "
        f"Tried: {package_dir / 'staking-cli'}, "
        f"installed package location, and current directory."
    )

cli_dir = find_cli_directory()
sys.path.insert(0, str(cli_dir))
# Change to the CLI directory so relative imports work
original_cwd = os.getcwd()
try:
    os.chdir(cli_dir)
    from main import StakingCLI
finally:
    os.chdir(original_cwd)


def main():
    """Entry point for the staking-cli console script."""
    StakingCLI().main()


if __name__ == "__main__":
    main()
