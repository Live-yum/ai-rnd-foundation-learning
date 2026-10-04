"""Driver contract for real-current-gate rereview and bounded diagnostics."""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "scenario",
    [
        "fresh",
        "stale",
        "stale-unlocked",
        "stale-expired",
        "invalid",
        "redacted",
        "drain-late",
        "drain-failed",
        "drain-expired",
    ],
)
def test_delivery_browser_review_contract(scenario):
    script = r"""
const assert = require('node:assert/strict');
const { deliveryFacts, requireDeliveryFacts, rereviewDelivery, observeRunRefreshes } = require(process.argv[1]);
const scenario = process.argv[2];
const gate = {stage:'delivery',can_approve:true,actions:['approve'],gate_id:'a'.repeat(64),digest:'b'.repeat(64),version:1,data:{sha256:'c'.repeat(64)}};
const run = {status:'WAITING_DELIVERY',auto_mode:false,pending:gate};
const report = {
  'delivery.json': {sha256:'c'.repeat(64),validation_level:'runtime',cleanroom:{passed:true,http:true,restart:true,database:'real-isolated-sqlite'}},
  'verification.json': {passed:true,source_digest:'d'.repeat(64),browser:{passed:true,real_browser:true}},
};
(async () => {
  if (scenario.startsWith('drain-')) {
    const { EventEmitter } = require('node:events');
    const page = new EventEmitter();
    let applied = false;
    page.evaluate = async () => {applied = true;};
    const tracker = observeRunRefreshes(page,'test-run');
    const request = {method:()=>'GET',url:()=>'http://127.0.0.1/runs/test-run/report'};
    page.emit('request',request);
    if (scenario === 'drain-expired') {
      await assert.rejects(tracker.drain(Date.now()-1), /existing browser deadline/);
      assert.equal(applied,false);
    } else {
      const pending = tracker.drain(Date.now()+1000);
      page.emit('response',request);
      await Promise.resolve();
      assert.equal(applied,false,'Response headers must not count as a finished refresh');
      page.emit(scenario === 'drain-failed' ? 'requestfailed' : 'requestfinished',request);
      await pending;
      assert.equal(applied,true);
    }
    tracker.close();
    assert.equal(page.listenerCount('request'),0);
    assert.equal(page.listenerCount('requestfinished'),0);
    assert.equal(page.listenerCount('requestfailed'),0);
    return;
  }
  const facts = deliveryFacts(run, report);
  requireDeliveryFacts(facts);
  if (scenario === 'invalid') {
    for (const name of Object.keys(facts)) {
      assert.throws(() => requireDeliveryFacts({...facts,[name]:null}), /Missing delivery prerequisite/);
      assert.throws(() => requireDeliveryFacts({...facts,[name]:false}), /Missing delivery prerequisite/);
    }
    const blocked = deliveryFacts({...run,pending:{...gate,can_approve:false}}, report);
    assert.throws(() => requireDeliveryFacts(blocked), /can_approve/);
    const changed = deliveryFacts(run, {...report,'delivery.json':{...report['delivery.json'],sha256:'e'.repeat(64)}});
    assert.throws(() => requireDeliveryFacts(changed), /gate_artifact_matches/);
    return;
  }
  if (scenario === 'redacted') {
    const secret = 'DO-NOT-SAVE-ARBITRARY-API-CONTENT';
    const data = deliveryFacts({status:secret,auto_mode:secret,pending:{stage:secret,gate_id:secret,digest:secret,version:secret,data:{sha256:secret},actions:[secret]}},
      {'delivery.json':{sha256:secret,validation_level:secret,cleanroom:{database:secret,error:secret}},'verification.json':{source_digest:secret,message:secret}});
    assert(!JSON.stringify(data).includes(secret));
    assert(Object.values(data).every(value => value === null || typeof value === 'boolean'));
    assert(JSON.stringify(data).length < 1500);
    return;
  }
  const events = [];
  const stale = scenario.startsWith('stale');
  const page = {
    getByRole(role, {name,exact}) {
      assert.equal(exact,true);
      if (role === 'button' && name === '查看最新版本') return {
        isVisible:async()=>stale,
        click:async()=>events.push('explicit-rereview'),
        waitFor:async({state})=>{assert.equal(state,'hidden');events.push('stale-cleared');},
      };
      assert.equal(role,'checkbox');assert.equal(name,'我已阅读本次验收证据与交付等级');
      return {isDisabled:async()=>{events.push('stale-locked');return scenario !== 'stale-unlocked';},check:async()=>assert.fail('Rereview must not acknowledge or approve')};
    },
    evaluate:async(callback,hash)=>{assert.equal(hash,'run/test-run/delivery');events.push('delivery-evidence');},
  };
  if (scenario === 'stale-expired') {
    await assert.rejects(() => rereviewDelivery(page,'test-run',Date.now()-1), /existing browser deadline/);
    assert.deepEqual(events,[]);
    return;
  }
  if (scenario === 'stale-unlocked') {
    await assert.rejects(() => rereviewDelivery(page,'test-run'), /stale delivery cannot be acknowledged/);
    assert.deepEqual(events,['stale-locked']);
    return;
  }
  assert.equal(await rereviewDelivery(page,'test-run'),stale);
  assert.deepEqual(events,stale ? ['stale-locked','explicit-rereview','stale-cleared','delivery-evidence'] : []);
})().catch(error=>{console.error(error);process.exitCode=1;});
"""
    driver = Path(__file__).resolve().parents[1] / "scripts/guided_browser.cjs"
    result = subprocess.run(
        ["node", "-e", script, str(driver), scenario],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
