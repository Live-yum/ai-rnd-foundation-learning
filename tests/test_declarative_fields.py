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
