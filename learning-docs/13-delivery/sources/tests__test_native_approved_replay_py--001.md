# tests/test_native_approved_replay.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.domain`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_exact_approved_replay_preserves_original_schema_and_bytes`（L35–L48）：接收`name`、`template`、`size`、`sha256`、`run_id`、`source_sha`。 控制顺序：L40断言`len(raw) == size`；L41断言`hashlib.sha256(raw).hexdigest() == sha256`；L43断言`plan == Plan.model_validate_json(raw)`；L44断言`{entity.name for entity in plan.entities} == {"customers", "requests", "tasks"}`；L45断言`{role.name for role in plan.business.roles} == {"manager", "service", "employee"}`；L47断言`run_id in note and source_sha in note`；L48断言`"never reads this fixture" in note`。 调用`(ROOT / record["path"]).read_bytes`、`len`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`replay.approved_customer_replay`、`Plan.model_validate_json`、`(ROOT / "tests/fixtures/customer_approved_replays/README.md").rea…`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_replay_rejects_untrusted_payload_before_generation`（L54–L84）：接收`tmp_path`、`monkeypatch`、`kind`。 控制顺序：L57按`kind == "oversize"`分支；L59按`kind == "schema"`分支；L61按`kind == "credential"`分支；L63按`kind == "candidate_envelope"`分支；L84断言`"secret-test-canary" not in str(caught.value)`。 调用`json.loads`、`(ROOT / original["path"]).read_text`、`json.dumps(data).encode`、`json.dumps`、`path.write_bytes`、`monkeypatch.setattr`、`monkeypatch.setitem`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_replay_template_is_not_read_from_fixture`（L87–L89）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`replay.approved_customer_replay`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_replay_workflow_is_separate_and_has_unique_artifacts`（L92–L104）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L94断言`"--approved-replay yudao-1d7" in source`；L95断言`"--approved-replay fastapi-0e8" in source`；L96断言`"--spec examples/plans/customer-service.json" in source`；L97断言`"native-runtime-${{ matrix.template }}-${{ matrix.case }}" in source`；L98断言`source.count("case: canonical") == 2`；L99断言`source.count("case: approved-1d7") == 1`；L100断言`source.count("case: approved-0e8") == 1`；L101断言`not re.search(r"^\s*(?:API_KEY\|BASE_URL)\s*:", source, re.M)`。后续分支沿下方源码相同行号继续阅读。 调用`(ROOT / ".github/workflows/customer-runtime.yml").read_text`、`source.count`、`re.search`、`(ROOT / "scripts/ci_real_model.py").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_approved_replay.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L104。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4036`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_approved_replay.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3954c3279c9f6f6c669668c60822a2dbf7a01541474478d15153ec69bc828e19"} -->
````python
# tests/test_native_approved_replay.py
"""Approved-plan provenance checks precede native generation; never a model substitute."""

import hashlib
import json
import re

import pytest

from scripts import ci_native_bundled as replay
from workbench.domain import Plan
from workbench.settings import ROOT


@pytest.mark.parametrize(
    "name,template,size,sha256,run_id,source_sha",
    [
        (
            "yudao-1d7",
            "yudao-vben",
            19534,
            "16731f7c60a15916058d64c503525aafe93e1c53e0da62bae1eb8d0c227730f5",
            "36795375784",
            "1d7c70b03e63509830e97af9af398c0bd148902e",
        ),
        (
            "fastapi-0e8",
            "fastapiadmin",
            19099,
            "023ed6b43f20de90ef3b68033263212204314c2df0be08095fd6f9ec9e56dcb4",
            "36826237130",
            "0e8ebdd0c74a86538b648d55b9fe56dcc71a9de9",
        ),
    ],
)
def test_exact_approved_replay_preserves_original_schema_and_bytes(
    name, template, size, sha256, run_id, source_sha
):
    record = replay.APPROVED_CUSTOMER_REPLAYS[name]
    raw = (ROOT / record["path"]).read_bytes()
    assert len(raw) == size
    assert hashlib.sha256(raw).hexdigest() == sha256
    plan = replay.approved_customer_replay(name, template)
    assert plan == Plan.model_validate_json(raw)
    assert {entity.name for entity in plan.entities} == {"customers", "requests", "tasks"}
    assert {role.name for role in plan.business.roles} == {"manager", "service", "employee"}
    note = (ROOT / "tests/fixtures/customer_approved_replays/README.md").read_text(encoding="utf-8")
    assert run_id in note and source_sha in note
    assert "never reads this fixture" in note


@pytest.mark.parametrize(
    "kind", ["digest", "oversize", "schema", "credential", "candidate_envelope"]
)
def test_approved_replay_rejects_untrusted_payload_before_generation(tmp_path, monkeypatch, kind):
    original = replay.APPROVED_CUSTOMER_REPLAYS["yudao-1d7"]
    data = json.loads((ROOT / original["path"]).read_text(encoding="utf-8"))
    if kind == "oversize":
        data["acceptance"] = ["x" * 140000]
    elif kind == "schema":
        data["entities"] = "not-an-entity-list"
    elif kind == "credential":
        data["acceptance"] = ["DATABASE_PASSWORD=secret-test-canary"]
    elif kind == "candidate_envelope":
        data = {
            "approval_status": "unapproved",
            "execution_authorized": False,
            "candidate_plan": data,
        }
    raw = json.dumps(data).encode()
    path = tmp_path / "fixture.json"
    path.write_bytes(raw)
    monkeypatch.setattr(replay, "ROOT", tmp_path)
    monkeypatch.setitem(
        replay.APPROVED_CUSTOMER_REPLAYS,
        "test",
        {
            "path": path.name,
            "template": "yudao-vben",
            "sha256": "0" * 64 if kind == "digest" else hashlib.sha256(raw).hexdigest(),
        },
    )
    with pytest.raises(ValueError) as caught:
        replay.approved_customer_replay("test", "yudao-vben")
    assert "secret-test-canary" not in str(caught.value)


def test_approved_replay_template_is_not_read_from_fixture():
    with pytest.raises(ValueError, match="template/path"):
        replay.approved_customer_replay("yudao-1d7", "fastapiadmin")


def test_replay_workflow_is_separate_and_has_unique_artifacts():
    source = (ROOT / ".github/workflows/customer-runtime.yml").read_text(encoding="utf-8")
    assert "--approved-replay yudao-1d7" in source
    assert "--approved-replay fastapi-0e8" in source
    assert "--spec examples/plans/customer-service.json" in source
    assert "native-runtime-${{ matrix.template }}-${{ matrix.case }}" in source
    assert source.count("case: canonical") == 2
    assert source.count("case: approved-1d7") == 1
    assert source.count("case: approved-0e8") == 1
    assert not re.search(r"^\s*(?:API_KEY|BASE_URL)\s*:", source, re.M)
    genuine = (ROOT / "scripts/ci_real_model.py").read_text(encoding="utf-8")
    assert "customer_approved_replays" not in genuine
    assert "approved_customer_replay" not in genuine
````
