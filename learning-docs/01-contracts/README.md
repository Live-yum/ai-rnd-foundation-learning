# 01 · 配置与数据合同

[总目录](../README.md) · [上一阶段](../00-environment/README.md) · [下一阶段](../02-storage/README.md)

## 先写边界，再写功能

从 `local_only.py` 开始：`local_http_url` 接受回环服务，拒绝公网、局域网、URL凭据和查询参数；模型地址由 `ModelProfile.validate_endpoint` 单独校验，允许远程 HTTPS。两类地址规则分开，才能做到“模型可以外部推理，其余工具本地运行”，而不是一刀切地禁网或放网。

`Settings` 把环境配置变成类型化对象。四个模型阶段依次是 requirements、planning、coding、review。`model_for` 决定哪些值可以继承，`public` 决定哪些值可以显示。尤其要读“地址改变但阶段密钥为空”分支：拒绝复用默认密钥，是在请求发出前阻止跨服务泄露。`_env_file=None` 只是不读个人 `.env`；进程环境变量仍然有效，遇到意外配置时检查当前终端，不要打印密钥排错。

`template_adapters.py` 提供模板合同，`catalog.py` 的选择校验直接导入它；两者必须在本阶段一同写入，再运行合同练习。它们固定后端、前端、数据库的合法组合，基础选择校验不启动后续原生服务。`domain.py` 不把字典原样转交后续工具，而是校验项目名、字段类型、保留名称、枚举、示例与批准动作。`BusinessSpec` 提前落盘，是因为 `Plan` 在导入时直接引用它；提前实现合同不代表现在就已经拥有角色和流程运行时。此时只理解“业务行为要能声明与验证”，第10阶段再把这些声明变成数据库事务。

## 保存并运行第一个合同练习

保存为 `.learning/checks/01_contracts.py`。这不是产品代码，而是你对刚写模块提出的可重复问题。

```python
# .learning/checks/01_contracts.py
from pydantic import ValidationError
from workbench.catalog import Selection
from workbench.domain import FieldSpec, digest
from workbench.settings import Settings

chosen = Selection(template="python-basic")
assert (chosen.frontend, chosen.database) == ("simple-admin", "sqlite")
for create in (
    lambda: Selection(template="yudao-vben", database="sqlite"),
    lambda: FieldSpec(name="title", kind="text", min_length=81, max_length=80),
):
    try:
        create()
    except ValidationError:
        pass
    else:
        raise AssertionError("invalid contract was accepted")
assert digest({"a": 1, "b": 2}) == digest({"b": 2, "a": 1})
settings = Settings(
    base_url="https://one.example/v1",
    api_key="exercise-only",
    model="demo",
    planning_base_url="https://two.example/v1",
    planning_api_key="",
    _env_file=None,
)
try:
    settings.model_for("planning")
except ValueError:
    print("01 PASS: valid selection; invalid contracts and cross-provider key reuse rejected")
else:
    raise AssertionError("a different provider requires its own key")
```

```bash
# .learning/commands/01-check.sh
uv run python .learning/checks/01_contracts.py
```

应出现一行以 `01 PASS` 开头的文字；示例地址没有被请求，字符串 `exercise-only` 只是本地假值。把一个断言临时反过来应得到 `AssertionError`，改回后再继续。不要删断言来获得绿色结果。

现在不要运行 `pytest tests/test_contracts.py`：pytest 会先加载全局 `tests/conftest.py`，它顶层导入 Store，而 Store 是下一站。这种隐藏依赖比“测试文件名叫合同测试”更能决定何时可执行。也不要调用 `Selection.capabilities()`，其业务能力展开在下一批模块完成后才可用。

## 本阶段源码和后续依赖

本阶段首次创建 7 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
