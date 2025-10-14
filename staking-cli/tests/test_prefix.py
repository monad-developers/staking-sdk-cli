import pytest
from src.helpers import is_valid_bls_private_key

BLS_PRIV_NO_PREFIX = "1f8b8a9d3c4e5f112233445566778899aabbccddeeff00112233445566778899"
BLS_PRIV_WITH_PREFIX = "0x" + BLS_PRIV_NO_PREFIX

def test_accepts_0x_prefixed_hex():
    assert is_valid_bls_private_key(BLS_PRIV_WITH_PREFIX) is True

def test_rejects_hex_without_prefix():
    assert is_valid_bls_private_key(BLS_PRIV_NO_PREFIX) is False

@pytest.mark.parametrize("bad", ["0X" + BLS_PRIV_NO_PREFIX, "0xGG", None, []])
def test_rejects_invalid_inputs(bad):
    assert is_valid_bls_private_key(bad) is False

def test_accepts_int():
    assert is_valid_bls_private_key(int(BLS_PRIV_NO_PREFIX, 16)) is True