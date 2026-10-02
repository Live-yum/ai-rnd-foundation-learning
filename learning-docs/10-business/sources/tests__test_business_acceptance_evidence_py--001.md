# tests/test_business_acceptance_evidence.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `customer_plan`（L16–L19）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`。 返回路径：L17的`Plan.model_validate_json( (ROOT / "examples/plans/customer-service.json").read_text(encodi…`。
- `execute`（L22–L31）：接收`product`。 调用`subprocess.run`、`clean_env`、`os.environ.get`。 返回路径：L23的`subprocess.run( [sys.executable, "verify.py", "--python", sys.executable], cwd=product, en…`。
- `test_customer_delivery_exposes_executed_field_relation_datetime_due_and_audit_proof`（L34–L113）：接收`tmp_path`。 控制顺序：L41断言`result.returncode == 0`；L44断言`proof["version"] == 1`；L45断言`len(proof["field_validation"]) == sum(len(entity.fields) for entity in plan.entities)`；L47遍历`("customers", "requests", "tasks")`；L49遍历`definition.fields`；L51按`entry.get("protected_create_rejected")`分支；L52断言`entry["protected_update_rejected"]`；L54按`field.required`分支。后续分支沿下方源码相同行号继续阅读。 调用`customer_plan`、`generate_basic`、`execute`、`json.loads`、`result.stdout.splitlines`、`len`、`sum`、`next`、`entry.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delivery_verifier_rejects_real_generated_runtime_faults`（L153–L169）：接收`tmp_path`、`file`、`old`、`new`、`expected`。 控制顺序：L164断言`old in text`；L167断言`result.returncode == 1`；L169断言`report["passed"] is False and expected.lower() in report["message"].lower()`。 调用`generate_basic`、`customer_plan`、`source.read_text`、`source.write_text`、`text.replace`、`execute`、`json.loads`、`result.stdout.splitlines`、`expected.lower`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delivery_verifier_rejects_audit_mutation_route_even_for_manager`（L172–L190）：接收`tmp_path`。 控制顺序：L186断言`result.returncode == 1`；L187断言`"Audit mutation/deletion route accepted" in json.loads(result.stdout.splitlines()[-1]…`。 调用`generate_basic`、`customer_plan`、`source.write_text`、`source.read_text`、`execute`、`json.loads`、`result.stdout.splitlines`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_acceptance_evidence.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L190。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6866`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_acceptance_evidence.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3bd55f666b0604f6cedec0b02d50b1a53aa8408bdf42432f7b4d13c9c8c4a9f0"} -->
````python
# tests/test_business_acceptance_evidence.py
"""Live generated-product proof and deliberate faults for customer delivery evidence."""

import json
import os
import subprocess
import sys

import pytest

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.settings import ROOT
from workbench.tools import clean_env


def customer_plan():
    return Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )


def execute(product):
    return subprocess.run(
        [sys.executable, "verify.py", "--python", sys.executable],
        cwd=product,
        env=clean_env({"PATH": os.environ.get("PATH", ""), "PYTHONUTF8": "1"}),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=150,
    )


def test_customer_delivery_exposes_executed_field_relation_datetime_due_and_audit_proof(tmp_path):
    plan = customer_plan()
    product = tmp_path / "product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    result = execute(product)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout.splitlines()[-1])
    proof = report["business"]["evidence"]
    assert proof["version"] == 1
    assert len(proof["field_validation"]) == sum(len(entity.fields) for entity in plan.entities)
    by_field = {(item["entity"], item["field"]): item for item in proof["field_validation"]}
    for entity in ("customers", "requests", "tasks"):
        definition = next(item for item in plan.entities if item.name == entity)
        for field in definition.fields:
            entry = by_field[entity, field.name]
            if entry.get("protected_create_rejected"):
                assert entry["protected_update_rejected"]
            else:
                if field.required:
                    assert entry["missing_required_rejected"] and entry["null_rejected"]
                if field.kind == "text":
                    assert (
                        entry["max_length"] == field.max_length
                        and entry["over_max_length_rejected"]
                    )
                if field.kind == "enum":
                    assert entry["invalid_enum_rejected"] and entry["declared_choices"] == len(
                        field.choices
                    )
    assert any(
        item["entity"] == "customers" and "requests" in item["target_entities"]
        for item in proof["related_views"]
    )
    assert any(
        item["entity"] == "requests" and "tasks" in item["target_entities"]
        for item in proof["related_views"]
    )
    assert any(
        item["role"] == "employee" and item["entity"] == "customers" and item["target_row_acl"]
        for item in proof["related_views"]
    )
    assert {item["field"] for item in proof["relation_labels"]} >= {
        "customer_id",
        "request_id",
        "assignee_id",
    }
    assert len(proof["datetime_policy"]) == 4
    assert all(
        item["timestamp_stored"]
        and item["excluded_from_keyword_search"]
        and set(item["undeclared_query_parameters_rejected"]) == {"filter", "from", "to"}
        for item in proof["datetime_policy"]
    )
    assert {item["entity"] for item in proof["due_notifications"]} == {"requests", "tasks"}
    assert all(
        item["past_due_events_verified"] > 0
        and item["future_deadline_no_event"]
        and item["repeated_reads_deduplicated"]
        and item["event_and_read_state_persisted_after_restart"]
        for item in proof["due_notifications"]
    )
    assert {item["entity"] for item in proof["audit_immutability"]} == {
        "customers",
        "requests",
        "tasks",
    }
    assert all(
        item["mutation_delete_attempts_rejected"] == 6
        and item["action_actor_timestamp"]
        and item["unchanged_after_attempts"]
        and item["archive_and_restart_preserved"]
        for item in proof["audit_immutability"]
    )
    assert len(json.dumps(proof).encode()) < 24000
    assert not any(
        secret in json.dumps(proof)
        for secret in ("Bearer", "password", "verify-manager", "record_id")
    )


@pytest.mark.parametrize(
    "file,old,new,expected",
    [
        ("business_policy.py", '<= field["max_length"]', "<= 1000000", "over_max_length_rejected"),
        (
            "business_policy.py",
            'if kind == "enum" and value not in field["choices"]:',
            "if False:",
            "invalid_enum_rejected",
        ),
        (
            "business_runtime.py",
            '*scope(actor, source, "read"),',
            "",
            "Related view violated target row ACL",
        ),
        (
            "business_runtime.py",
            'row.get("name") or row.get("title") or "关联记录"',
            'row["id"]',
            "Reference labels",
        ),
        (
            "querying.py",
            'if field.get("searchable")',
            'if field.get("searchable") or field["kind"] == "datetime"',
            "Nonsearchable datetime",
        ),
        (
            "querying.py",
            'if field.get("date_range"):',
            'if field.get("date_range") or field["kind"] == "datetime":',
            "expected 422",
        ),
        ("business_runtime.py", "target.c[due] <= utc(),", "", "notifications"),
    ],
)
def test_delivery_verifier_rejects_real_generated_runtime_faults(
    tmp_path, file, old, new, expected
):
    product = tmp_path / "product"
    generate_basic(
        customer_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    source = product / file
    text = source.read_text(encoding="utf-8")
    assert old in text
    source.write_text(text.replace(old, new), encoding="utf-8")
    result = execute(product)
    assert result.returncode == 1, result.stdout + result.stderr
    report = json.loads(result.stdout.splitlines()[-1])
    assert report["passed"] is False and expected.lower() in report["message"].lower(), report


def test_delivery_verifier_rejects_audit_mutation_route_even_for_manager(tmp_path):
    product = tmp_path / "product"
    generate_basic(
        customer_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    source = product / "app.py"
    source.write_text(
        source.read_text(encoding="utf-8")
        + '\n@app.put("/api/{entity}/{identity}/history")\ndef mutable_audit(entity: str, identity: str):\n    return {"modified": True}\n',
        encoding="utf-8",
    )
    result = execute(product)
    assert result.returncode == 1, result.stdout + result.stderr
    assert (
        "Audit mutation/deletion route accepted"
        in json.loads(result.stdout.splitlines()[-1])["message"]
    )
````
