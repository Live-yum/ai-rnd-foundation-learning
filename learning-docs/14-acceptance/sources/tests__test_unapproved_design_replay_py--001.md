# tests/test_unapproved_design_replay.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_real_model`、`workbench.domain`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ContractStore`（L18–L52）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ContractStore.__init__`（L19–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Requirement( summary="客户服务", users=["管理人员", "服务人员"], data_scope="…`、`Requirement`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ContractStore.get_run`（L42–L44）：接收`run_id`。 调用`self.calls.append`、`deepcopy`。 返回路径：L44的`deepcopy(self.run)`。
- `ContractStore.latest_revision`（L46–L52）：接收`run_id`、`stage`。 调用`self.calls.append`、`deepcopy`。 返回路径：L48的`{"requirement": deepcopy(self.requirement)} if stage == "requirements" else {"plan": deepc…`。
- `save`（L55–L58）：接收`store`、`path`、`secret`。 调用`preserve_unapproved_design_contract`、`DiagnosticTextBudget`。 返回路径：L56的`preserve_unapproved_design_contract( store, "synthetic-run", path, DiagnosticTextBudget(se…`。
- `test_failure_contract_is_exact_bounded_and_not_a_generation_input`（L61–L77）：接收`tmp_path`。 控制顺序：L66断言`receipt["status"] == "saved" and receipt["execution_authorized"] is False`；L67断言`receipt["bytes"] <= MAX_REPLAY_PLAN_BYTES`；L69断言`payload["approval_status"] == "unapproved"`；L70断言`payload["purpose"] == "offline_contract_validation_only"`；L71断言`payload["execution_authorized"] is False`；L72断言`payload["requirement"] == Requirement.model_validate(store.requirement).model_dump()`；L73断言`payload["candidate_plan"] == Plan.model_validate(store.plan).model_dump()`；L76断言`(store.requirement, store.plan, store.run) == original`。后续分支沿下方源码相同行号继续阅读。 调用`ContractStore`、`deepcopy`、`save`、`json.loads`、`path.read_text`、`Requirement.model_validate(store.requirement).model_dump`、`Requirement.model_validate`、`Plan.model_validate(store.plan).model_dump`、`Plan.model_validate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonfailure_cannot_write_unapproved_contract`（L81–L86）：接收`tmp_path`、`state`。 控制顺序：L85断言`save(store, target) == {"status": "not_failure"}`；L86断言`not target.exists()`。 调用`ContractStore`、`save`、`target.exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_outer_acceptance_failure_retains_exact_contract_without_execution_approval`（L90–L105）：接收`tmp_path`、`state`。 控制顺序：L99断言`receipt["status"] == "saved"`；L101断言`payload["execution_authorized"] is False`；L102断言`payload["requirement"] == store.requirement`；L103断言`payload["candidate_plan"] == Plan.model_validate(store.plan).model_dump()`。 调用`ContractStore`、`preserve_unapproved_design_contract`、`DiagnosticTextBudget`、`json.loads`、`target.read_text`、`Plan.model_validate(store.plan).model_dump`、`Plan.model_validate`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_outer_failure_flag_cannot_be_coerced`（L109–L116）：接收`tmp_path`、`flag`。 控制顺序：L113断言`preserve_unapproved_design_contract( store, "synthetic-run", target, DiagnosticTextBu…`；L116断言`not target.exists()`。 调用`ContractStore`、`preserve_unapproved_design_contract`、`DiagnosticTextBudget`、`target.exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ready_outer_failure_still_rejects_secrets`（L119–L131）：接收`tmp_path`。 控制顺序：L124断言`preserve_unapproved_design_contract( store, "synthetic-run", target, DiagnosticTextBu…`；L131断言`not target.exists()`。 调用`ContractStore`、`preserve_unapproved_design_contract`、`DiagnosticTextBudget`、`target.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_both_contract_strings_and_structural_secrets_are_rejected`（L144–L152）：接收`tmp_path`、`secret`。 控制顺序：L148断言`save(store, target) == {"status": "secret_scan_rejected"}`；L149断言`not target.exists()`；L151断言`save(store, target) == {"status": "secret_scan_rejected"}`；L152断言`not target.exists()`。 调用`ContractStore`、`save`、`target.exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_normalized_schema_is_rejected`（L156–L161）：接收`tmp_path`、`which`。 控制顺序：L160断言`save(store, target) == {"status": "invalid_schema"}`；L161断言`not target.exists()`。 调用`ContractStore`、`getattr`、`save`、`target.exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oversized_contract_is_rejected_without_truncating_or_persisting`（L164–L169）：接收`tmp_path`。 控制顺序：L168断言`save(store, target) == {"status": "size_limit"}`；L169断言`not target.exists()`。 调用`ContractStore`、`save`、`target.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_out_of_scope_or_missing_contract_never_uses_other_data`（L172–L180）：接收`tmp_path`。 控制顺序：L176断言`save(store, target) == {"status": "outside_customer_scope"}`；L179断言`save(store, target) == {"status": "unavailable"}`；L180断言`not target.exists()`。 调用`ContractStore`、`save`、`target.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_artifact_is_failure_only_with_distinct_nonexecutable_path`（L183–L191）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L188断言`"if: failure()" in section`；L189断言`"path: reports/real-model/unapproved-design-contract.json" in section`；L190断言`"retention-days: 7" in section`；L191断言`"run:" not in section`。 调用`(ROOT / ".github/workflows/native-probe.yml").read_text`、`source.split("- name: Retain unapproved normalized design", 1)[1]…`、`source.split`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_unapproved_design_replay.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L191。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7349`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_unapproved_design_replay.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bd69945ddb890f66f42c0f5f7d2ea9bee536dbc720e0bc74e2c7e28874cf6924"} -->
````python
# tests/test_unapproved_design_replay.py
"""Failure diagnostics preserve exact contracts without conferring execution approval."""

import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from scripts.ci_real_model import (
    MAX_REPLAY_PLAN_BYTES,
    DiagnosticTextBudget,
    preserve_unapproved_design_contract,
)
from workbench.domain import Plan, Requirement
from workbench.settings import ROOT


class ContractStore:
    def __init__(self):
        self.run = {"status": "BLOCKED", "template": "yudao-vben"}
        self.requirement = Requirement(
            summary="客户服务",
            users=["管理人员", "服务人员"],
            data_scope="shared",
            features=[],
            acceptance=[],
            facts={
                "metrics": [
                    {
                        "name": "requests_total",
                        "entity": "requests",
                        "role_scope": ["manager", "service"],
                    }
                ]
            },
        ).model_dump()
        self.plan = json.loads(
            (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
        )
        self.calls = []

    def get_run(self, run_id):
        self.calls.append(("get_run", run_id))
        return deepcopy(self.run)

    def latest_revision(self, run_id, stage):
        self.calls.append(("latest_revision", run_id, stage))
        return (
            {"requirement": deepcopy(self.requirement)}
            if stage == "requirements"
            else {"plan": deepcopy(self.plan)}
        )


def save(store, path, secret="exact-key-canary"):
    return preserve_unapproved_design_contract(
        store, "synthetic-run", path, DiagnosticTextBudget(secrets=(secret,), limit=0)
    )


def test_failure_contract_is_exact_bounded_and_not_a_generation_input(tmp_path):
    store = ContractStore()
    original = deepcopy(store.requirement), deepcopy(store.plan), deepcopy(store.run)
    path = tmp_path / "unapproved-design-contract.json"
    receipt = save(store, path)
    assert receipt["status"] == "saved" and receipt["execution_authorized"] is False
    assert receipt["bytes"] <= MAX_REPLAY_PLAN_BYTES
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["approval_status"] == "unapproved"
    assert payload["purpose"] == "offline_contract_validation_only"
    assert payload["execution_authorized"] is False
    assert payload["requirement"] == Requirement.model_validate(store.requirement).model_dump()
    assert payload["candidate_plan"] == Plan.model_validate(store.plan).model_dump()
    with pytest.raises(ValidationError):
        Plan.model_validate(payload)
    assert (store.requirement, store.plan, store.run) == original
    assert all(call[0] in {"get_run", "latest_revision"} for call in store.calls)


@pytest.mark.parametrize("state", ["READY", "SOURCE_READY", "WAITING_DESIGN", "RUNNING"])
def test_nonfailure_cannot_write_unapproved_contract(tmp_path, state):
    store = ContractStore()
    store.run["status"] = state
    target = tmp_path / "unapproved-design-contract.json"
    assert save(store, target) == {"status": "not_failure"}
    assert not target.exists()


@pytest.mark.parametrize("state", ["READY", "SOURCE_READY"])
def test_outer_acceptance_failure_retains_exact_contract_without_execution_approval(
    tmp_path, state
):
    store = ContractStore()
    store.run["status"] = state
    target = tmp_path / "unapproved-design-contract.json"
    receipt = preserve_unapproved_design_contract(
        store, "synthetic-run", target, DiagnosticTextBudget(), acceptance_failed=True
    )
    assert receipt["status"] == "saved"
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["execution_authorized"] is False
    assert payload["requirement"] == store.requirement
    assert payload["candidate_plan"] == Plan.model_validate(store.plan).model_dump()
    with pytest.raises(ValidationError):
        Plan.model_validate(payload)


@pytest.mark.parametrize("flag", [False, "true", 1, None])
def test_outer_failure_flag_cannot_be_coerced(tmp_path, flag):
    store = ContractStore()
    store.run["status"] = "READY"
    target = tmp_path / "unapproved-design-contract.json"
    assert preserve_unapproved_design_contract(
        store, "synthetic-run", target, DiagnosticTextBudget(), acceptance_failed=flag
    ) == {"status": "not_failure"}
    assert not target.exists()


def test_ready_outer_failure_still_rejects_secrets(tmp_path):
    store = ContractStore()
    store.run["status"] = "READY"
    store.requirement["facts"]["example"] = "exact-key-canary"
    target = tmp_path / "unapproved-design-contract.json"
    assert preserve_unapproved_design_contract(
        store,
        "synthetic-run",
        target,
        DiagnosticTextBudget(secrets=("exact-key-canary",)),
        acceptance_failed=True,
    ) == {"status": "secret_scan_rejected"}
    assert not target.exists()


@pytest.mark.parametrize(
    "secret",
    [
        "exact-key-canary",
        "Authorization: Bearer opaque-token",
        "password=hidden-value",
        "https://user:hidden-value@example.invalid",
        "sk-credentialcanary12345",
    ],
)
def test_both_contract_strings_and_structural_secrets_are_rejected(tmp_path, secret):
    store = ContractStore()
    store.requirement["facts"]["description"] = secret
    target = tmp_path / "unapproved-design-contract.json"
    assert save(store, target) == {"status": "secret_scan_rejected"}
    assert not target.exists()
    store.requirement["facts"] = {"configuration": {"password": "hidden-value"}}
    assert save(store, target) == {"status": "secret_scan_rejected"}
    assert not target.exists()


@pytest.mark.parametrize("which", ["requirement", "plan"])
def test_malformed_normalized_schema_is_rejected(tmp_path, which):
    store = ContractStore()
    getattr(store, which)["provider_headers"] = {"x": "not selected"}
    target = tmp_path / "unapproved-design-contract.json"
    assert save(store, target) == {"status": "invalid_schema"}
    assert not target.exists()


def test_oversized_contract_is_rejected_without_truncating_or_persisting(tmp_path):
    store = ContractStore()
    store.requirement["facts"]["large"] = "A" * (MAX_REPLAY_PLAN_BYTES + 1)
    target = tmp_path / "unapproved-design-contract.json"
    assert save(store, target) == {"status": "size_limit"}
    assert not target.exists()


def test_out_of_scope_or_missing_contract_never_uses_other_data(tmp_path):
    store = ContractStore()
    target = tmp_path / "unapproved-design-contract.json"
    store.run["template"] = "unrelated"
    assert save(store, target) == {"status": "outside_customer_scope"}
    store.run["template"] = "python-basic"
    store.plan = None
    assert save(store, target) == {"status": "unavailable"}
    assert not target.exists()


def test_artifact_is_failure_only_with_distinct_nonexecutable_path():
    source = (ROOT / ".github/workflows/native-probe.yml").read_text(encoding="utf-8")
    section = source.split("- name: Retain unapproved normalized design", 1)[1].split("- name:", 1)[
        0
    ]
    assert "if: failure()" in section
    assert "path: reports/real-model/unapproved-design-contract.json" in section
    assert "retention-days: 7" in section
    assert "run:" not in section
````
