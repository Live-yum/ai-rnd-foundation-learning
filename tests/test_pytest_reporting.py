"""Bound report identifiers while preserving exact adversarial test inputs."""

import hashlib

import pytest
from conftest import pytest_make_parametrize_id


@pytest.mark.parametrize("value", [None, 7, {}, "ordinary", b"ordinary", "x" * 80])
def test_ordinary_ids_remain_pytest_defaults(value):
    assert pytest_make_parametrize_id(None, value, "payload") is None


@pytest.mark.parametrize(
    "value", ["x" * 81, b"x" * 81, "中" * 100, "\ud800" * 100, b"x" * 2_000_001]
)
def test_large_ids_are_bounded_deterministic_and_input_is_unchanged(value):
    original = value
    raw = value.encode("utf-8", errors="surrogatepass") if isinstance(value, str) else value
    result = pytest_make_parametrize_id(None, value, "payload")
    assert (
        result
        == f"payload-{type(value).__name__}-{len(value)}-{hashlib.sha256(raw).hexdigest()[:16]}"
    )
    assert len(result) < 80
    assert value is original
    assert pytest_make_parametrize_id(None, value, "payload") == result
