"""Pinned local snapshot lookup contracts; real service acceptance runs separately."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scripts import daytona_bootstrap as bootstrap

NAME = "rnd-python-0123456789abcdef"
IMAGE = "registry:6000/rnd-python:0123456789abcdef"


def snapshot(**overrides):
    return SimpleNamespace(name=NAME, image_name=IMAGE, state="active", **overrides)


def page(number, items, total_pages=1):
    return SimpleNamespace(page=number, items=items, total_pages=total_pages)


def test_exact_name_lookup_reads_every_page_and_never_uses_uuid_route():
    wanted = snapshot()
    service = Mock()
    service.list.side_effect = [
        page(1, [SimpleNamespace(name=NAME + "-other")], 3),
        page(2, [wanted], 3),
        page(3, [], 3),
    ]
    assert bootstrap.snapshot_named(service, NAME) is wanted
    assert [call.kwargs for call in service.list.call_args_list] == [
        {"page": number, "limit": 100} for number in range(1, 4)
    ]
    service.get.assert_not_called()
    service.create.assert_not_called()


@pytest.mark.parametrize("total_pages", [0, 1])
def test_confirmed_empty_listing_means_absent(total_pages):
    service = Mock()
    service.list.return_value = page(1, [], total_pages)
    assert bootstrap.snapshot_named(service, NAME) is None


@pytest.mark.parametrize("result", [page(2, []), page(1, [], -1), page(1, [], 101)])
def test_invalid_or_excessive_pagination_fails_closed(result):
    service = Mock()
    service.list.return_value = result
    with pytest.raises(ValueError, match="分页"):
        bootstrap.snapshot_named(service, NAME)
    service.create.assert_not_called()


def test_duplicate_names_across_pages_are_not_guessed():
    service = Mock()
    service.list.side_effect = [page(1, [snapshot()], 2), page(2, [snapshot()], 2)]
    with pytest.raises(ValueError, match="多个同名"):
        bootstrap.snapshot_named(service, NAME)


def test_listing_failure_is_not_interpreted_as_absence():
    service = Mock()
    service.list.side_effect = RuntimeError("explicit local authentication failure")
    with pytest.raises(RuntimeError, match="authentication"):
        bootstrap.snapshot_named(service, NAME)
    service.create.assert_not_called()


@pytest.fixture
def worker(tmp_path, monkeypatch):
    (tmp_path / "snapshot-image.json").write_text(
        json.dumps({"image": IMAGE, "snapshot": NAME}), encoding="utf-8"
    )
    (tmp_path / "api-key.json").write_text(
        json.dumps({"value": "local-test-key-not-a-real-credential"}), encoding="utf-8"
    )
    client = Mock()
    client.snapshot.list.return_value = page(1, [])
    client.snapshot.create.return_value = snapshot()
    monkeypatch.setattr(bootstrap, "install_loopback_guard", lambda: None)
    monkeypatch.setattr(bootstrap, "client_for", lambda settings: client)
    return tmp_path, client


@pytest.mark.parametrize("reuse", [False, True])
def test_worker_creates_or_reuses_only_matching_active_local_snapshot(worker, reuse):
    directory, client = worker
    if reuse:
        client.snapshot.list.return_value = page(1, [snapshot()])
    bootstrap.snapshot_worker(directory)
    client.snapshot.get.assert_not_called()
    if reuse:
        client.snapshot.create.assert_not_called()
    else:
        params = client.snapshot.create.call_args.args[0]
        assert params.name == NAME and params.image == IMAGE and params.region_id == "local"
        assert client.snapshot.create.call_args.kwargs == {"timeout": 600}
    env = (directory / "workbench.env").read_text(encoding="utf-8")
    assert "DAYTONA_API_URL=http://127.0.0.1:3000/api" in env
    assert f"DAYTONA_SNAPSHOT={NAME}" in env
    client.close.assert_called_once()


@pytest.mark.parametrize("reuse", [False, True])
@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("name", "other", "来源"),
        ("image_name", "other:image", "来源"),
        ("state", "building", "尚未就绪"),
        ("state", "build_failed", "尚未就绪"),
    ],
)
def test_worker_never_writes_ready_config_for_wrong_or_unready_snapshot(
    worker, monkeypatch, reuse, field, value, message
):
    directory, client = worker
    invalid = snapshot()
    setattr(invalid, field, value)
    # Inject the lookup result to test validation independently of exact-name filtering.
    monkeypatch.setattr(bootstrap, "snapshot_named", lambda *args: invalid if reuse else None)
    client.snapshot.create.return_value = invalid
    with pytest.raises(ValueError, match=message):
        bootstrap.snapshot_worker(directory)
    assert not (directory / "workbench.env").exists()
    client.close.assert_called_once()


def test_worker_preserves_existing_credentials_and_closes_on_list_failure(worker):
    directory, client = worker
    existing = "DAYTONA_API_KEY=existing-local-test-key\n"
    (directory / "workbench.env").write_text(existing, encoding="utf-8")
    client.snapshot.list.side_effect = RuntimeError("explicit local service failure")
    with pytest.raises(RuntimeError, match="service"):
        bootstrap.snapshot_worker(directory)
    assert (directory / "workbench.env").read_text(encoding="utf-8") == existing
    client.snapshot.create.assert_not_called()
    client.close.assert_called_once()
