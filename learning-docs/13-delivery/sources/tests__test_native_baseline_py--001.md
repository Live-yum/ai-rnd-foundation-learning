# tests/test_native_baseline.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.native_checks`、`workbench.native_environment`、`workbench.native_frontend`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_native_database_is_loopback_dedicated`（L23–L25）：接收`url`。 调用`pytest.raises`、`checked_database`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_database_valid`（L28–L29）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L29断言`checked_database(URL).database == "test_codegen"`。 调用`checked_database`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_env_never_inherits_model_key`（L32–L40）：接收`tmp_path`、`monkeypatch`。 控制顺序：L36断言`env["ENVIRONMENT"] == "dev"`；L37断言`env["DEBUG"] == "False"`；L38断言`env["SCHEDULER_ALLOW_CODE_EXEC"] == "False"`；L39断言`"API_KEY" not in clean_env(env)`；L40断言`"BASE_URL" not in clean_env(env)`。 调用`monkeypatch.setenv`、`native_environment`、`clean_env`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_yudao_profile_uses_real_auth`（L43–L51）：接收`tmp_path`。 控制顺序：L47断言`"yudao.security.mock-enable=false" in text`；L48断言`"spring.datasource.dynamic.druid.validation-query=SELECT 1" in text`；L49断言`"${NATIVE_DB_PASSWORD}" in text`；L50断言`"example" not in text`；L51断言`env["NATIVE_DB_PASSWORD"] == "example"`。 调用`native_environment`、`path.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_copy_excludes_environment_and_refuses_overwrite`（L54–L64）：接收`tmp_path`。 控制顺序：L61断言`(destination / "main.py").exists()`；L62断言`not (destination / ".env").exists()`。 调用`source.mkdir`、`(source / "main.py").write_text`、`(source / ".env").write_text`、`copy_source`、`(destination / "main.py").exists`、`(destination / ".env").exists`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_menu_page_and_button_can_share_permission`（L67–L74）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L74断言`read_menu_ids(rows, "read") == [1, 2, 3]`。 调用`read_menu_ids`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_menu_parent_cycle_rejected`（L77–L80）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`read_menu_ids`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_denial_accepts_http_or_application_status`（L84–L89）：接收`status`、`code`。 控制顺序：L89断言`not successful(response)`。 调用`httpx.Response`、`httpx.Request`、`denied`、`successful`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_denial_does_not_accept_server_failure`（L92–L97）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`httpx.Response`、`httpx.Request`、`pytest.raises`、`denied`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_mock_services_are_disabled`（L100–L104）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L102断言`env["VITE_NITRO_MOCK"] == "false"`；L103断言`env["VITE_GLOB_API_URL"] == "/admin-api"`；L104断言`env["VITE_APP_CAPTCHA_ENABLE"] == "false"`。 调用`frontend_environment`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_baseline.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L104。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3864`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_baseline.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7fa5614b53fbeec7fed13616c663d913766db31732fe6f3b3a29eed2085412ee"} -->
````python
# tests/test_native_baseline.py
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
````
