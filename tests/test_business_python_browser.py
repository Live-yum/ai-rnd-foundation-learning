"""Actual Chromium checks of the extended existing lightweight admin UI."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from test_business_python import runtime_plan

from workbench.generator import generate_basic
from workbench.tools import clean_env

DRIVER = r"""
const assert=require('node:assert/strict');
const [url,modulePath]=process.argv.slice(2);
(async()=>{
 const {chromium}=require(modulePath);const browser=await chromium.launch({headless:true});
 const page=await browser.newPage();page.setDefaultTimeout(15000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try {
  async function login(username){if(page.url().startsWith(url)){await Promise.all([page.waitForEvent('load'),page.locator('#logout').click()]);}else await page.goto(url);await page.locator('#auth input[name=username]').fill(username);await page.locator('#auth input[name=password]').fill('Example-Test-Password-123');await page.locator('#auth button[type=submit]').click();await page.locator('#workspace').waitFor({state:'visible'});}
  async function choose(name){await page.locator('#entities button').filter({hasText:name}).click();await page.waitForTimeout(150);}
  await login('admin');assert(await page.locator('#business-admin').isVisible());
  await choose('Customers');await page.locator('#create').click();await page.locator('#record input[name=name]').fill('Browser customer');await page.locator('#record button[type=submit]').click();await page.locator('#editor').waitFor({state:'hidden'});await page.locator('#rows tr').waitFor();
  await login('employee-a');assert(await page.locator('#business-admin').isHidden());await choose('Requests');await page.locator('#create').click();await page.locator('#record select[name=customer_id]').selectOption({label:'Browser customer'});await page.locator('#record input[name=due_at]').fill('2020-01-01T00:00');assert.equal(await page.locator('#record [name=request_state]').count(),0);await page.locator('#record button[type=submit]').click();await page.locator('#editor').waitFor({state:'hidden'});await page.locator('#rows tr').waitFor();
  await login('admin');await choose('Requests');await page.getByRole('button',{name:'详情 / 处理'}).click();await page.locator('#business-detail').waitFor({state:'visible'});await page.locator('#business-assignee').selectOption({label:'service-a'});await page.locator('#business-actions').getByRole('button',{name:'分配',exact:true}).click();await page.waitForTimeout(150);await page.locator('#business-close').click();
  await login('service-a');await choose('Requests');assert(await page.locator('#create').isHidden());await page.getByRole('button',{name:'详情 / 处理'}).click();await page.locator('#business-detail').waitFor({state:'visible'});await page.locator('#business-actions').getByRole('button',{name:'start',exact:true}).click();await page.locator('#business-actions').getByRole('button',{name:'resolve',exact:true}).waitFor();await page.locator('#business-note-form textarea').fill('Browser service note');await page.locator('#business-note-form button').click();await page.locator('#business-notes').getByText(/Browser service note/).waitFor();await page.locator('#business-actions').getByRole('button',{name:'resolve',exact:true}).click();await page.waitForTimeout(200);await page.locator('#business-close').click();
  await login('employee-a');await choose('Requests');assert((await page.locator('#rows').innerText()).includes('resolved'));await page.getByRole('button',{name:'详情 / 处理'}).click();await page.locator('#business-detail').waitFor({state:'visible'});assert.equal(await page.locator('#business-actions button').count(),0);assert((await page.locator('#business-notes').innerText()).includes('Browser service note'));await page.locator('#business-close').click();
  await login('employee-b');await choose('Requests');assert.equal(await page.locator('#rows tr').count(),0);await choose('Customers');await page.getByRole('button',{name:'详情 / 处理'}).click();await page.locator('#business-detail').waitFor({state:'visible'});assert.equal(await page.locator('#business-related p').count(),0);assert.deepEqual(errors,[]);
  console.log(JSON.stringify({passed:true,roles:3,actual_browser:true,assignment:true,transitions:true,notes:true,row_isolation:true}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
"""


def test_business_roles_in_actual_lightweight_ui(tmp_path):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual browser tooling not configured; required in Actions")
    product = tmp_path / "product"
    generate_basic(runtime_plan(), product)
    env = clean_env(
        {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_DATA_DIR": str(tmp_path / "db"),
            "PYTHONUTF8": "1",
            "PLAYWRIGHT_BROWSERS_PATH": "0",
        }
    )
    init = subprocess.run(
        [sys.executable, "manage.py", "init"],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert init.returncode == 0, init.stdout + init.stderr
    setup = """import getpass
getpass.getpass=lambda _: 'Example-Test-Password-123'
import manage
manage.bootstrap_admin('admin')
from app import password_hash
from schema import engine,metadata
from sqlalchemy import insert
import uuid
with engine.begin() as connection:
 for name,role in [('employee-a','employee'),('employee-b','employee'),('service-a','service')]:
  connection.execute(insert(metadata.tables['users']).values(id=str(uuid.uuid4()),username=name,password=password_hash('Example-Test-Password-123'),role=role))
"""
    result = subprocess.run(
        [sys.executable, "-c", setup],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "critical",
        ],
        cwd=product,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        url = f"http://127.0.0.1:{port}"
        for _ in range(100):
            try:
                if httpx.get(url + "/health", trust_env=False).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        script = tmp_path / "business-browser.cjs"
        script.write_text(DRIVER, encoding="utf-8")
        result = subprocess.run(
            ["node", str(script), url, module],
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert '"passed":true' in result.stdout
    finally:
        process.terminate()
        process.wait(timeout=10)
