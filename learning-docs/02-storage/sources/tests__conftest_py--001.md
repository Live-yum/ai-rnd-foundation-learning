# tests/conftest.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.settings`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `settings`（L11–L12）：接收`tmp_path`。 调用`Settings`。 返回路径：L12的`Settings(data_dir=tmp_path / "state", install_products=False, _env_file=None)`。
- `store`（L16–L20）：接收`settings`。 调用`Store`、`value.migrate`、`value.engine.dispose`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `plan`（L24–L42）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate`。 返回路径：L25的`Plan.model_validate( { "title": "任务管理", "data_scope": "per_user", "acceptance": ["CRUD 和两用…`。
- `requirement`（L45–L53）：接收`questions`、`scope`。 调用`Requirement`。 返回路径：L46的`Requirement( summary="任务管理", users=["个人用户"], data_scope=scope, features=["CRUD"], acceptan…`。
- `FixtureGateway`（L56–L91）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `FixtureGateway.__init__`（L59–L63）：接收`plan`、`require_question`、`fail_first_code`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `FixtureGateway.complete`（L65–L91）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L67按`schema is Requirement`分支；L71按`schema is Plan`分支；L73按`schema is Patches`分支；L75按`self.fail_first_code and key == "coding:0"`分支；L91抛异常，停止当前正常路径。 调用`self.calls.append`、`requirement`、`Patches.model_validate`、`AssertionError`。 返回路径：L68的`requirement( ["谁使用？"] if self.require_question and key == "requirement:1" else [] )`；L72的`self.plan`；L77的`Patches.model_validate( { "explanation": "test fixture rule", "patches": [ { "path": "cust…`。
- `new_run`（L94–L98）：接收`store`、`template`。 调用`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`。 返回路径：L96的`store.create_run( project["id"], {"requirement": "个人任务 CRUD", "template": template}, str(u…`。
- `decision`（L101–L112）：接收`store`、`run_id`、`action`、`text`。 调用`store.get_run`、`store.submit`、`str`、`uuid.uuid4`。 返回路径：L103的`store.submit( run_id, { "gate_id": pending["gate_id"], "action": action, "approved": True …`。

</details>

**创建路径：** `tests/conftest.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L112。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3517`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/conftest.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d143624b6d22736af4bfe3f4895fec6cefc2def026e5eaeb2a98f3545d819563"} -->
````python
# tests/conftest.py
import uuid

import pytest

from workbench.domain import Patches, Plan, Requirement
from workbench.settings import Settings
from workbench.store import Store


@pytest.fixture
def settings(tmp_path):
    return Settings(data_dir=tmp_path / "state", install_products=False, _env_file=None)


@pytest.fixture
def store(settings):
    value = Store(settings)
    value.migrate()
    yield value
    value.engine.dispose()


@pytest.fixture
def plan():
    return Plan.model_validate(
        {
            "title": "任务管理",
            "data_scope": "per_user",
            "acceptance": ["CRUD 和两用户隔离"],
            "entities": [
                {
                    "name": "task",
                    "description": "任务",
                    "fields": [
                        {"name": "title", "kind": "text", "max_length": 80},
                        {"name": "priority", "kind": "integer"},
                        {"name": "done", "kind": "boolean"},
                    ],
                }
            ],
        }
    )


def requirement(questions=None, scope="per_user"):
    return Requirement(
        summary="任务管理",
        users=["个人用户"],
        data_scope=scope,
        features=["CRUD"],
        acceptance=["CRUD 与数据隔离"],
        questions=questions or [],
    )


class FixtureGateway:
    """Explicit test double: never used by rnd start or live mode."""

    def __init__(self, plan, require_question=False, fail_first_code=False):
        self.plan = plan
        self.require_question = require_question
        self.fail_first_code = fail_first_code
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append(key)
        if schema is Requirement:
            return requirement(
                ["谁使用？"] if self.require_question and key == "requirement:1" else []
            )
        if schema is Plan:
            return self.plan
        if schema is Patches:
            content = "def validate(entity, data):\n    if entity == 'task' and data['priority'] < 0:\n        raise ValueError('priority must be nonnegative')\n"
            if self.fail_first_code and key == "coding:0":
                content = "def validate(entity, data):\n    return None\n"
            return Patches.model_validate(
                {
                    "explanation": "test fixture rule",
                    "patches": [
                        {
                            "path": "custom_rules.py",
                            "before_sha256": payload["context"]["files"]["custom_rules.py"][
                                "sha256"
                            ],
                            "content": content,
                        }
                    ],
                }
            )
        raise AssertionError(schema)


def new_run(store, template="python-basic"):
    project = store.create_project("task", str(uuid.uuid4()))
    return store.create_run(
        project["id"], {"requirement": "个人任务 CRUD", "template": template}, str(uuid.uuid4())
    )["run_id"]


def decision(store, run_id, action="approve", text=""):
    pending = store.get_run(run_id)["pending"]
    return store.submit(
        run_id,
        {
            "gate_id": pending["gate_id"],
            "action": action,
            "approved": True if action == "approve" else False if action == "reject" else None,
            "text": text,
        },
        str(uuid.uuid4()),
    )
````
