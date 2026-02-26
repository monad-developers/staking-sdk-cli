# hooks/hook-rich.py
from PyInstaller.utils.hooks import collect_submodules

# Collect all submodules from rich, including the Unicode data modules
# that are dynamically imported at runtime
hiddenimports = collect_submodules('rich')
