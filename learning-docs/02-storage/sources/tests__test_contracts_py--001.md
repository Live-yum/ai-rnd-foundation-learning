# tests/test_contracts.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_bad_title`（L9–L11）：接收`value`。 调用`pytest.raises`、`ProjectInput`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_role_not_user_controlled`（L14–L16）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`RunInput.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_strict_approval`（L20–L22）：接收`value`。 调用`pytest.raises`、`ResumeInput`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reserved_fields`（L26–L28）：接收`name`。 调用`pytest.raises`、`FieldSpec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_digest_canonical`（L31–L32）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L32断言`digest({"a": 1, "b": 2}) == digest({"b": 2, "a": 1})`。 调用`digest`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_path_independent`（L35–L38）：接收`tmp_path`、`monkeypatch`。 控制顺序：L38断言`settings.data_dir == ROOT / "local-data"`。 调用`monkeypatch.chdir`、`Settings`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_three_env_names`（L41–L49）：接收`tmp_path`。 控制顺序：L48断言`settings.model == "test-model"`；L49断言`"never-print" not in repr(settings)`。 调用`env.write_text`、`Settings`、`settings.require_model`、`repr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_remote_plain_http_rejected`（L52–L56）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`Settings( base_url="http://example.test/v1", api_key="x", model="…`、`Settings`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_plan_duplicate_and_scope`（L59–L63）：接收`plan`。 调用`plan.model_dump`、`pytest.raises`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_contracts.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L63。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1940`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_contracts.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e03b5575c6e058941e5efd2c4dd45bc1ad3697c1851eb07466071203a037bd87"} -->
````python
# tests/test_contracts.py
import pytest
from pydantic import ValidationError

from workbench.domain import FieldSpec, Plan, ProjectInput, ResumeInput, RunInput, digest
from workbench.settings import ROOT, Settings


@pytest.mark.parametrize("value", ["", "   ", "a" * 201])
def test_bad_title(value):
    with pytest.raises(ValidationError):
        ProjectInput(title=value)


def test_role_not_user_controlled():
    with pytest.raises(ValidationError):
        RunInput.model_validate({"requirement": "x", "role": "system"})


@pytest.mark.parametrize("value", ["true", "false", 1, 0, None])
def test_strict_approval(value):
    with pytest.raises(ValidationError):
        ResumeInput(gate_id="a" * 64, action="approve", approved=value)


@pytest.mark.parametrize("name", ["../../x", "id", "owner_id", "class", "BadName"])
def test_reserved_fields(name):
    with pytest.raises(ValidationError):
        FieldSpec(name=name, kind="text")


def test_digest_canonical():
    assert digest({"a": 1, "b": 2}) == digest({"b": 2, "a": 1})


def test_path_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = Settings(data_dir="local-data", _env_file=None)
    assert settings.data_dir == ROOT / "local-data"


def test_three_env_names(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        "BASE_URL=https://example.test/v1\nAPI_KEY=never-print\nMODE=test-model\n", encoding="utf-8"
    )
    settings = Settings(_env_file=env)
    settings.require_model()
    assert settings.model == "test-model"
    assert "never-print" not in repr(settings)


def test_remote_plain_http_rejected():
    with pytest.raises(ValueError):
        Settings(
            base_url="http://example.test/v1", api_key="x", model="x", _env_file=None
        ).require_model()


def test_plan_duplicate_and_scope(plan):
    data = plan.model_dump()
    data["entities"] *= 2
    with pytest.raises(ValidationError):
        Plan.model_validate(data)
````
