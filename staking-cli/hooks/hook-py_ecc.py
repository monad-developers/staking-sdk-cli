# hooks/hook-py_ecc.py
from PyInstaller.utils.hooks import copy_metadata 

# This line tells PyInstaller to find and collect all metadata 
# associated with the 'py_ecc' package.
datas = copy_metadata('py_ecc')
