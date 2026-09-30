"""Negative contracts; real-model success is only proved by the dedicated workflow."""

import hashlib

import pytest

from scripts import ci_local_embeddings as local


def test_local_model_requires_exact_weight_identity(tmp_path):
    (tmp_path / "onnx").mkdir()
    (tmp_path / "onnx/model.onnx").write_bytes(b"not an inference model")
    (tmp_path / "tokenizer.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="pinned official ONNX"):
        local.check_weights(tmp_path)


def test_local_model_requires_matching_tokenizer_identity(tmp_path, monkeypatch):
    data = b"test bytes only for negative identity check"
    (tmp_path / "onnx").mkdir()
    (tmp_path / "onnx/model.onnx").write_bytes(data)
    (tmp_path / "tokenizer.json").write_bytes(b"{}")
    monkeypatch.setattr(local, "WEIGHT_SHA", hashlib.sha256(data).hexdigest())
    with pytest.raises(ValueError, match="tokenizer"):
        local.check_weights(tmp_path)


def test_missing_weights_cannot_be_replaced_with_fixture(tmp_path):
    with pytest.raises(FileNotFoundError):
        local.check_weights(tmp_path)
