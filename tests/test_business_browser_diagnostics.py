"""Bounded failure callsites without exposing real browser values or credentials."""

import json
import shutil
import subprocess

import pytest

from workbench.settings import ROOT


@pytest.mark.parametrize("separator", ["/", "\\"])
@pytest.mark.parametrize("name", ["TimeoutError", "Error with private-canary"])
@pytest.mark.parametrize("operation", ["locator.click", "page.goto", "unknown.private-canary"])
def test_browser_failure_retains_only_allowlisted_operation_and_static_callsites(
    name, operation, separator
):
    script = r"""
const {browserFailure}=require('./templates/product/verify-business-browser.cjs');
const [name,operation,separator]=process.argv.slice(1);
const message=operation+': Timeout; private-canary password token DOM http://private.invalid/';
const frame='    at caller ('+['private-canary','account','verify-business-browser.cjs:42:7)'].join(separator);
const result=browserFailure({name,message,stack:message+'\n'+Array(20).fill(frame).join('\n')});
console.log(result);
"""
    result = subprocess.run(
        [shutil.which("node"), "-e", script, name, operation, separator],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=20,
    ).stdout.strip()
    code, encoded = result.split(" ", 1)
    assert code == ("TimeoutError" if name == "TimeoutError" else "BusinessBrowserFailure")
    report = json.loads(encoded)
    assert report == {
        "source": "verify-business-browser.cjs",
        "operation": operation if operation != "unknown.private-canary" else None,
        "callsites": [{"line": 42, "column": 7}] * 5,
    }
    assert len(result) < 400
    assert not any(secret in result for secret in ("private-canary", "password", "token", "http:"))


def test_business_failure_codes_remain_specific_without_fake_callsites():
    result = subprocess.run(
        [
            shutil.which("node"),
            "-e",
            "const {browserFailure}=require('./templates/product/verify-business-browser.cjs');"
            "console.log(browserFailure({message:'business-browser-relation-list-label'}));",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=20,
    ).stdout.strip()
    code, encoded = result.split(" ", 1)
    assert code == "business-browser-relation-list-label"
    assert json.loads(encoded)["callsites"] == []
