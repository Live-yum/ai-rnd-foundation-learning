# tests/test_tools_cli.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.cli`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_clean_environment`（L10–L13）：接收`monkeypatch`。 控制顺序：L11遍历`["API_KEY", "BASE_URL", "MODE", "NATIVE_FASTAPIADMIN_TOKEN"]`；L13断言`not {"API_KEY", "BASE_URL", "MODE", "NATIVE_FASTAPIADMIN_TOKEN"} & clean_env().keys()`。 调用`monkeypatch.setenv`、`clean_env().keys`、`clean_env`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fixed_command_exit_and_timeout`（L16–L21）：接收`tmp_path`。 控制顺序：L17断言`run_command([sys.executable, "-c", "print(42)"], tmp_path)["returncode"] == 0`。 调用`run_command`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cli_discovery`（L24–L29）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L26断言`runner.invoke(app, ["--help"]).exit_code == 0`；L28断言`result.exit_code == 0`；L29断言`"native-source-export" in result.output`。 调用`CliRunner`、`runner.invoke`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_clean_environment_preserves_windows_runtime_without_model_credentials`（L32–L40）：接收`monkeypatch`。 控制顺序：L37断言`next(value for key, value in env.items() if key.upper() == "SYSTEMROOT") == r"C:\Wind…`；L38断言`env["WINDIR"] == r"C:\Windows"`；L39断言`env["PRODUCT_DATA_DIR"] == "isolated-product-data"`；L40断言`"API_KEY" not in env`。 调用`monkeypatch.setenv`、`clean_env`、`next`、`env.items`、`key.upper`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_tools_cli.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L40。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1618`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_tools_cli.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "706eb97e66b8de6453218dce7ccb73e1a8fe1dee6e379e2b3ba3aaef8b5e638b"} -->
````python
# tests/test_tools_cli.py
import sys

import pytest
from typer.testing import CliRunner

from workbench.cli import app
from workbench.tools import ToolFailure, clean_env, run_command


def test_clean_environment(monkeypatch):
    for key in ["API_KEY", "BASE_URL", "MODE", "NATIVE_FASTAPIADMIN_TOKEN"]:
        monkeypatch.setenv(key, "sensitive")
    assert not {"API_KEY", "BASE_URL", "MODE", "NATIVE_FASTAPIADMIN_TOKEN"} & clean_env().keys()


def test_fixed_command_exit_and_timeout(tmp_path):
    assert run_command([sys.executable, "-c", "print(42)"], tmp_path)["returncode"] == 0
    with pytest.raises(ToolFailure):
        run_command([sys.executable, "-c", "raise SystemExit(7)"], tmp_path)
    with pytest.raises(ToolFailure):
        run_command([sys.executable, "-c", "import time; time.sleep(10)"], tmp_path, timeout=0.1)


def test_cli_discovery():
    runner = CliRunner()
    assert runner.invoke(app, ["--help"]).exit_code == 0
    result = runner.invoke(app, ["templates"])
    assert result.exit_code == 0
    assert "native-source-export" in result.output


def test_clean_environment_preserves_windows_runtime_without_model_credentials(monkeypatch):
    monkeypatch.setenv("SystemRoot", r"C:\Windows")
    monkeypatch.setenv("WINDIR", r"C:\Windows")
    monkeypatch.setenv("API_KEY", "must-not-enter-product-process")
    env = clean_env({"PRODUCT_DATA_DIR": "isolated-product-data"})
    assert next(value for key, value in env.items() if key.upper() == "SYSTEMROOT") == r"C:\Windows"
    assert env["WINDIR"] == r"C:\Windows"
    assert env["PRODUCT_DATA_DIR"] == "isolated-product-data"
    assert "API_KEY" not in env
````
