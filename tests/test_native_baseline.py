"""Unit contracts supplement, never replace, native services in the baseline Actions job."""

import httpx
import pytest

from workbench.native_checks import denied, read_menu_ids, successful
from workbench.native_environment import checked_database, copy_source, native_environment
from workbench.native_frontend import frontend_environment
from workbench.tools import clean_env

URL = "postgresql+psycopg://native:example@127.0.0.1:5432/test_codegen"


@pytest.mark.parametrize(
    "url",
    [
        "sqlite:///example.db",
        "postgresql://user:pass@database.example/test_codegen",
        "postgresql://user:pass@127.0.0.1/production",
        "postgresql://user:pass@127.0.0.1/test%0aname_codegen",
    ],
)
def test_native_database_is_loopback_dedicated(url):
    with pytest.raises(ValueError):
        checked_database(url)


def test_native_database_valid():
    assert checked_database(URL).database == "test_codegen"


def test_native_env_never_inherits_model_key(tmp_path, monkeypatch):
    monkeypatch.setenv("API_KEY", "not-for-native-processes")
    monkeypatch.setenv("BASE_URL", "https://private-model.example")
    env = native_environment("fastapiadmin", tmp_path, URL, 8001)
    assert env["ENVIRONMENT"] == "dev"
    assert env["DEBUG"] == "False"
    assert env["SCHEDULER_ALLOW_CODE_EXEC"] == "False"
    assert "API_KEY" not in clean_env(env)
    assert "BASE_URL" not in clean_env(env)


def test_native_yudao_profile_uses_real_auth(tmp_path):
    env = native_environment("yudao-vben", tmp_path, URL, 48080)
    path = tmp_path / "yudao-server/src/main/resources/application-native.properties"
    text = path.read_text(encoding="utf-8")
    assert "yudao.security.mock-enable=false" in text
    assert "spring.datasource.dynamic.druid.validation-query=SELECT 1" in text
    assert "${NATIVE_DB_PASSWORD}" in text
    assert "example" not in text
    assert env["NATIVE_DB_PASSWORD"] == "example"


def test_native_copy_excludes_environment_and_refuses_overwrite(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "main.py").write_text("print('native')\n")
    (source / ".env").write_text("API_KEY=not-for-export\n")
    destination = tmp_path / "copy"
    copy_source(source, destination)
    assert (destination / "main.py").exists()
    assert not (destination / ".env").exists()
    with pytest.raises(FileExistsError):
        copy_source(source, destination)


def test_menu_page_and_button_can_share_permission():
    rows = [
        {"id": 1, "parent_id": None},
        {"id": 2, "parent_id": 1, "permission": "read"},
        {"id": 3, "parent_id": 2, "permission": "read"},
        {"id": 4, "parent_id": 2, "permission": "write"},
    ]
    assert read_menu_ids(rows, "read") == [1, 2, 3]


def test_menu_parent_cycle_rejected():
    rows = [{"id": 1, "parentId": 2, "permission": "read"}, {"id": 2, "parentId": 1}]
    with pytest.raises(AssertionError):
        read_menu_ids(rows, "read")


@pytest.mark.parametrize("status,code", [(401, 401), (403, 403), (200, 401), (200, 403)])
def test_native_denial_accepts_http_or_application_status(status, code):
    response = httpx.Response(
        status, json={"code": code}, request=httpx.Request("GET", "http://127.0.0.1/api")
    )
    denied(response)
    assert not successful(response)


def test_native_denial_does_not_accept_server_failure():
    response = httpx.Response(
        500, json={"code": 500}, request=httpx.Request("GET", "http://127.0.0.1/api")
    )
    with pytest.raises(AssertionError):
        denied(response)


def test_frontend_mock_services_are_disabled():
    env = frontend_environment("yudao-vben", "http://127.0.0.1:48080")
    assert env["VITE_NITRO_MOCK"] == "false"
    assert env["VITE_GLOB_API_URL"] == "/admin-api"
    assert env["VITE_APP_CAPTCHA_ENABLE"] == "false"  # Disposable local lab only.
