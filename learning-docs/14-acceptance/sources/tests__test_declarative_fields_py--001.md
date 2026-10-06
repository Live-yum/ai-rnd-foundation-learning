# tests/test_declarative_fields.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.requirement_coverage`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `order_plan`（L20–L37）：接收`**bounds`。 调用`Plan.model_validate`。 返回路径：L21的`Plan.model_validate( { "title": "订单", "data_scope": "per_user", "acceptance": ["订单数量必须大于0"…`。
- `test_numeric_requirement_cannot_pass_as_acceptance_text_only`（L41–L61）：接收`encoding`。 控制顺序：L49按`encoding == "typed"`分支；L56按`encoding == "fact"`分支；L59断言`coverage_gaps(requirement, order_plan(), diagnostics=diagnostics)`；L60断言`any(row["attribute"] in {"minimum", "exclusive_minimum"} for row in diagnostics)`；L61断言`not coverage_gaps(requirement, order_plan(minimum=1))`。 调用`Requirement`、`Requirement.model_validate`、`requirement.model_dump`、`coverage_gaps`、`order_plan`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_numeric_filter_is_not_a_save_constraint`（L64–L72）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L72断言`not any("minimum" in gap for gap in coverage_gaps(requirement, order_plan()))`。 调用`Requirement`、`any`、`coverage_gaps`、`order_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_constraints_reject_impossible_specs_and_enforce_boundaries`（L75–L107）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L76遍历`( {"name": "category", "kind": "enum", "max_length": 1, "choices"…`；L92遍历`(1, 4)`；L93断言`model(quantity=number).quantity == number`；L94遍历`(0, -1, -2, 5, 2**31, 9007199254740993, True)`；L105断言`pattern(code="A12").code == "A12"`。 调用`pytest.raises`、`FieldSpec.model_validate`、`input_model`、`order_plan(minimum=1, exclusive_maximum=5).entities[0].model_dump`、`order_plan`、`model`、`FieldSpec(name="code", kind="text", pattern="^A[0-9]+$", example=…`、`FieldSpec`、`pattern`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_product_checks_numeric_boundaries_and_datetime`（L110–L130）：接收`tmp_path`。 控制顺序：L127断言`result.returncode == 0`；L129断言`"integer-boundaries:orders.quantity" in proof["checks"]`；L130断言`"BETWEEN 2 AND 8" in (product / "database/schema.postgresql.sql").read_text()`。 调用`generate_basic`、`order_plan`、`clean_env`、`os.environ.get`、`subprocess.run`、`str`、`json.loads`、`result.stdout.splitlines`、`(product / "database/schema.postgresql.sql").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pattern_product_has_an_approved_positive_example`（L133–L151）：接收`tmp_path`。 控制顺序：L151断言`result.returncode == 0`。 调用`order_plan(minimum=1).model_dump`、`order_plan`、`raw["entities"][0]["fields"].append`、`generate_basic`、`Plan.model_validate`、`subprocess.run`、`str`、`clean_env`、`os.environ.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_rejects_unsafe_integer_and_preserves_untouched_datetime`（L155–L191）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L157按`not shutil.which("node") or not jsdom.exists()`分支；L191断言`result.returncode == 0`。 调用`shutil.which`、`jsdom.exists`、`pytest.skip`、`subprocess.run`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_declarative_fields.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L191。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7612`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_declarative_fields.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "89ca0d69cd16fb8e6de84ac56509d5ae4434df4eeb28e50d41f250b1984fc4c3"} -->
````python
# tests/test_declarative_fields.py
"""Regression for the review's text-only numeric rule and cross-layer field loss."""

import json
import os
import shutil
import subprocess
import sys

import pytest
from pydantic import ValidationError

from templates.product.fields import input_model
from workbench.domain import FieldSpec, Plan, Requirement
from workbench.generator import generate_basic
from workbench.requirement_coverage import coverage_gaps
from workbench.settings import ROOT
from workbench.tools import clean_env


def order_plan(**bounds):
    return Plan.model_validate(
        {
            "title": "订单",
            "data_scope": "per_user",
            "acceptance": ["订单数量必须大于0"],
            "entities": [
                {
                    "name": "orders",
                    "description": "订单",
                    "fields": [
                        {"name": "quantity", "kind": "integer", **bounds},
                        {"name": "happened", "kind": "datetime", "required": False},
                    ],
                }
            ],
        }
    )


@pytest.mark.parametrize("encoding", ["legacy", "typed", "fact"])
def test_numeric_requirement_cannot_pass_as_acceptance_text_only(encoding):
    requirement = Requirement(
        summary="订单",
        users=["用户"],
        data_scope="per_user",
        features=["CRUD"],
        acceptance=["orders.quantity 必须大于0，拒绝零和负数"],
    )
    if encoding == "typed":
        requirement = Requirement.model_validate(
            {
                **requirement.model_dump(),
                "field_requirements": [{"entity": "orders", "field": "quantity", "minimum": 1}],
            }
        )
    if encoding == "fact":
        requirement.facts = {"orders.quantity.minimum": 1}
    diagnostics = []
    assert coverage_gaps(requirement, order_plan(), diagnostics=diagnostics)
    assert any(row["attribute"] in {"minimum", "exclusive_minimum"} for row in diagnostics)
    assert not coverage_gaps(requirement, order_plan(minimum=1))


def test_numeric_filter_is_not_a_save_constraint():
    requirement = Requirement(
        summary="订单",
        users=["用户"],
        data_scope="per_user",
        features=["CRUD"],
        acceptance=["筛选 orders.quantity > 0"],
    )
    assert not any("minimum" in gap for gap in coverage_gaps(requirement, order_plan()))


def test_constraints_reject_impossible_specs_and_enforce_boundaries():
    for raw in (
        {"name": "category", "kind": "enum", "max_length": 1, "choices": ["a", "long"]},
        {"name": "quantity", "kind": "integer", "minimum": 1, "exclusive_maximum": 1},
        {"name": "title", "kind": "text", "minimum": 1},
        {"name": "code", "kind": "text", "pattern": "(a+)\\1", "example": "aa"},
        {
            "name": "code",
            "kind": "text",
            "pattern": "^A[0-9]+$",
            "example": "A12",
            "searchable": True,
        },
    ):
        with pytest.raises(ValidationError):
            FieldSpec.model_validate(raw)
    model = input_model(order_plan(minimum=1, exclusive_maximum=5).entities[0].model_dump())
    for number in (1, 4):
        assert model(quantity=number).quantity == number
    for number in (0, -1, -2, 5, 2**31, 9007199254740993, True):
        with pytest.raises(ValidationError):
            model(quantity=number)
    pattern = input_model(
        {
            "name": "item",
            "fields": [
                FieldSpec(name="code", kind="text", pattern="^A[0-9]+$", example="A12").model_dump()
            ],
        }
    )
    assert pattern(code="A12").code == "A12"
    with pytest.raises(ValidationError):
        pattern(code="B12")


def test_generated_product_checks_numeric_boundaries_and_datetime(tmp_path):
    product = tmp_path / "product"
    generate_basic(
        order_plan(minimum=2, maximum=8),
        product,
        {"template": "python-basic", "frontend": "api-only"},
    )
    env = clean_env({"PATH": os.environ.get("PATH", ""), "PYTHONUTF8": "1"})
    result = subprocess.run(
        [sys.executable, "verify.py", "--product", str(product)],
        cwd=product,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=100,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    proof = json.loads(result.stdout.splitlines()[-1])
    assert "integer-boundaries:orders.quantity" in proof["checks"]
    assert "BETWEEN 2 AND 8" in (product / "database/schema.postgresql.sql").read_text()


def test_pattern_product_has_an_approved_positive_example(tmp_path):
    raw = order_plan(minimum=1).model_dump()
    raw["entities"][0]["fields"].append(
        {"name": "code", "kind": "text", "pattern": "^A[0-9]+$", "example": "A12"}
    )
    product = tmp_path / "product"
    generate_basic(
        Plan.model_validate(raw), product, {"template": "python-basic", "frontend": "api-only"}
    )
    result = subprocess.run(
        [sys.executable, "verify.py", "--product", str(product)],
        cwd=product,
        env=clean_env({"PATH": os.environ.get("PATH", ""), "PYTHONUTF8": "1"}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=100,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.node_tools
def test_frontend_rejects_unsafe_integer_and_preserves_untouched_datetime():
    jsdom = ROOT / "ui/node_modules/jsdom"
    if not shutil.which("node") or not jsdom.exists():
        pytest.skip("UI Node dependencies are required")
    driver = r"""
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {JSDOM}=require(process.argv[1]);
const dom=new JSDOM(fs.readFileSync('templates/frontends/simple-admin/index.html','utf8'),{url:'http://localhost',runScripts:'outside-only'});
const w=dom.window;w.HTMLDialogElement.prototype.showModal=function(){};w.HTMLDialogElement.prototype.close=function(){};
const scenario=`
(async()=>{
 spec={entities:[]};entity={name:'orders',fields:[{name:'quantity',kind:'integer',required:true,minimum:2,maximum:8},{name:'happened',kind:'datetime',required:false}]};
 let submitted;
 api=async(path,options)=>{submitted=JSON.parse(options.body);return {json:async()=>[]}};load=async()=>{};
 await edit({id:'record',quantity:4,happened:'2026-01-01T03:03:34.123456Z'});
 const form=document.getElementById('record');
 await form.onsubmit({preventDefault(){}});
 const original=submitted.happened;
 submitted=null;form.elements.quantity.value='9007199254740993';
 await form.onsubmit({preventDefault(){}});
 const filter=control(entity.fields[0],'filter');
 return {original,submitted,message:document.getElementById('notice').textContent,minimum:form.elements.quantity.min,maximum:form.elements.quantity.max,filterMin:filter.min,filterMax:filter.max};
})()`;
Promise.resolve(w.eval(fs.readFileSync('templates/frontends/simple-admin/app.js','utf8')+scenario))
 .then(result=>{assert.equal(result.original,'2026-01-01T03:03:34.123456Z');assert.equal(result.submitted,null);assert.ok(result.message);assert.equal(result.minimum,'2');assert.equal(result.maximum,'8');assert.equal(result.filterMin,'-2147483648');assert.equal(result.filterMax,'2147483647');})
 .catch(error=>{console.error(error);process.exitCode=1}).finally(()=>dom.window.close());
"""
    result = subprocess.run(
        ["node", "-e", driver, str(jsdom)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
````
