# tests/test_native_frontend_lifecycle.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.generator`、`workbench.native`、`workbench.native_delivery`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_database_identity_does_not_retain_credentials`（L17–L24）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L20断言`"oldpassword" not in identity`。 调用`database_identity`、`check_database_identity`、`original.replace`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_catalog_config_does_not_claim_acceptance`（L27–L33）：接收`tmp_path`。 控制顺序：L31断言`entry["level"] == "managed-runtime"`；L32断言`entry["configured"] is True`；L33断言`entry["runtime_verified"] is False`。 调用`Settings`、`write_runtime_example`、`next`、`catalog`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_vben_public_build_config_excludes_credentials`（L36–L65）：接收`tmp_path`、`monkeypatch`。 控制顺序：L61断言`data["VITE_GLOB_API_URL"] == "/admin-api"`；L62断言`data["VITE_NITRO_MOCK"] == "false"`；L63断言`"API_KEY" not in data`；L64断言`"never-serialize-this" not in (app / ".env.production.example").read_text()`；L65断言`len(commands) == 3`。 调用`app.mkdir`、`(root / "pnpm-lock.yaml").write_text`、`(app / "dist").mkdir`、`(app / "dist/index.html").write_text`、`zipfile.ZipFile`、`(app / "vite.config.ts").write_bytes`、`archive.read`、`monkeypatch.setattr`、`native_frontend.frontend_environment`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_vben_public_build_config_excludes_credentials.tool`（L51–L53）：接收`command`、`cwd`、`timeout`、`env`、`**kwargs`。 调用`commands.append`。 返回路径：L53的`{"log": "fixture only", "returncode": 0}`。
- `test_full_vben_build_has_bounded_rust_parallelism`（L68–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L70断言`env["RAYON_NUM_THREADS"] == "2"`；L71断言`"8192" in env["NODE_OPTIONS"]`。 调用`native_frontend.frontend_environment`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_native_product_uses_approved_project_title`（L75–L79）：接收`template`。 控制顺序：L78断言`env["VITE_APP_TITLE"] == title`；L79断言`env["VITE_APP_TITLE"] != "Native lab"`。 调用`native_frontend.frontend_environment`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_frontend_lifecycle.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L79。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3304`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_frontend_lifecycle.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6bb5323ceece81d287deb94be4b66b88e2127cadfbf8102bf64e37eea00fff0f"} -->
````python
# tests/test_native_frontend_lifecycle.py
"""Local regressions are contracts, not native browser acceptance evidence."""

import pytest
from dotenv import dotenv_values

from workbench import native_frontend
from workbench.generator import PrerequisiteError
from workbench.native import catalog
from workbench.native_delivery import (
    check_database_identity,
    database_identity,
    write_runtime_example,
)
from workbench.settings import Settings


def test_database_identity_does_not_retain_credentials():
    original = "postgresql+psycopg://alice:oldpassword@127.0.0.1:5432/product_codegen"
    identity = database_identity(original)
    assert "oldpassword" not in identity
    receipt = {"database_identity": identity}
    check_database_identity(receipt, original.replace("oldpassword", "newpassword"))
    with pytest.raises(PrerequisiteError, match="数据库"):
        check_database_identity(receipt, original.replace("product_codegen", "other_codegen"))


def test_catalog_config_does_not_claim_acceptance(tmp_path):
    settings = Settings(data_dir=tmp_path, _env_file=None)
    write_runtime_example(settings, "fastapiadmin")
    entry = next(item for item in catalog(settings) if item["id"] == "fastapiadmin")
    assert entry["level"] == "managed-runtime"
    assert entry["configured"] is True
    assert entry["runtime_verified"] is False


def test_vben_public_build_config_excludes_credentials(tmp_path, monkeypatch):
    root = tmp_path / "frontend"
    app = root / "apps/web-antd"
    app.mkdir(parents=True)
    (root / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
    (app / "dist").mkdir()
    (app / "dist/index.html").write_text("<html></html>")
    import zipfile

    from workbench.settings import ROOT

    with zipfile.ZipFile(ROOT / "templates/vendor/yudao-frontend.zip") as archive:
        (app / "vite.config.ts").write_bytes(archive.read("apps/web-antd/vite.config.ts"))
    commands = []

    def tool(command, cwd, timeout, env, **kwargs):
        commands.append(command)
        return {"log": "fixture only", "returncode": 0}

    monkeypatch.setattr(native_frontend, "run_command", tool)
    monkeypatch.setattr(native_frontend, "prepare_vben_source", lambda *_: None)
    env = native_frontend.frontend_environment("yudao-vben", "http://127.0.0.1:48080")
    env["API_KEY"] = "never-serialize-this"
    native_frontend.build_frontend("yudao-vben", root, env, tmp_path / "reports")
    data = dotenv_values(app / ".env.production")
    assert data["VITE_GLOB_API_URL"] == "/admin-api"
    assert data["VITE_NITRO_MOCK"] == "false"
    assert "API_KEY" not in data
    assert "never-serialize-this" not in (app / ".env.production.example").read_text()
    assert len(commands) == 3


def test_full_vben_build_has_bounded_rust_parallelism():
    env = native_frontend.frontend_environment("yudao-vben", "http://127.0.0.1:48080")
    assert env["RAYON_NUM_THREADS"] == "2"
    assert "8192" in env["NODE_OPTIONS"]


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_generated_native_product_uses_approved_project_title(template):
    title = "内部客户服务管理平台"
    env = native_frontend.frontend_environment(template, "http://127.0.0.1:48080", title)
    assert env["VITE_APP_TITLE"] == title
    assert env["VITE_APP_TITLE"] != "Native lab"
````
