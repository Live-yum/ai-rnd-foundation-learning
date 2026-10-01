"""Native decorations must finish normally, without concealing business pixels."""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from workbench.settings import ROOT
from workbench.tools import clean_env

DRIVER = r"""
const assert = require('node:assert/strict'), http = require('node:http'), fs = require('node:fs');
const [mode, modulePath, filename] = process.argv.slice(1);
const { chromium } = require(modulePath);
const { dismissNativeThemeGuide, waitNativeDecorationsFinished, captureNativeScreenshot } = require('./scripts/business_fastapi_browser.cjs');
const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(`<!doctype html><meta charset="utf-8">
    <style>[hidden]{display:none!important}.el-popover{position:fixed;right:5px;top:5px;background:white}
      canvas.fixed{position:fixed;inset:0;pointer-events:none}#record{margin-top:100px}</style>
    <header id="app-header"><button class="setting-btn">Settings</button></header>
    <div class="el-popover">点击这里查看 主题风格</div>
    <div class="setting-modal"><div class="el-drawer" hidden>Native settings</div></div>
    <input id="query" value="EXACT-CUSTOMER"><select id="category"><option value="company">企业</option></select>
    <div id="record" data-record-id="121">Exact customer record 121</div><button id="business">Archive record</button>
    <canvas id="business-chart" width="100" height="30"></canvas>
    ${mode === 'no-canvas' || mode === 'guide-remains' ? '' : '<canvas id="decoration" class="fixed pointer-events-none" width="600" height="300"></canvas>'}
    <script>
      const mode = ${JSON.stringify(mode)};
      window.businessClicks=0;window.settingsClicks=0;window.bursts=0;
      const guide=document.querySelector('.el-popover'), drawer=document.querySelector('.el-drawer');
      document.querySelector('.setting-btn').onclick=()=>{window.settingsClicks++;guide.hidden=true;drawer.hidden=false};
      document.addEventListener('keydown',e=>{if(e.key==='Escape')drawer.hidden=true});
      document.querySelector('#business').onclick=()=>window.businessClicks++;
      const chart=document.querySelector('#business-chart').getContext('2d');chart.fillStyle='blue';chart.fillRect(0,0,100,30);
      const canvas=document.querySelector('#decoration');
      if(canvas){
        const context=canvas.getContext('2d');
        const burst=()=>{window.bursts++;context.fillStyle='red';context.fillRect(20,20,30,30)};
        const clear=()=>{context.clearRect(0,0,600,300);window.lastClear=Date.now()};
        burst();
        if(mode!=='persistent'){
          setTimeout(clear,100);
          // A later native burst must restart the quiet interval, not be frozen or removed.
          setTimeout(burst,900);setTimeout(clear,1100);
        }
      }
    </script>`);
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({headless:true});
  try{
    const page=await browser.newPage({viewport:{width:600,height:400}});page.setDefaultTimeout(2500);
    await page.goto('http://127.0.0.1:'+server.address().port);
    if(mode!=='guide-remains')await dismissNativeThemeGuide(page);
    if(mode==='persistent'){
      await assert.rejects(waitNativeDecorationsFinished(page,{timeout:350,quiet:100}),/did not finish/);
      assert(!fs.existsSync(filename));
    }else if(mode==='guide-remains'){
      await assert.rejects(captureNativeScreenshot(page,filename),/theme guide must be dismissed/);
      assert(!fs.existsSync(filename));
    }else{
      await captureNativeScreenshot(page,filename);assert(fs.statSync(filename).size>1000);
      assert.equal(await page.locator('.el-popover:visible').count(),0);
      assert.equal(await page.locator('.el-drawer:visible').count(),0);
    }
    const state=await page.evaluate(()=>{
      const canvas=document.querySelector('#decoration');
      return {query:document.querySelector('#query').value,category:document.querySelector('#category').value,
        record:document.querySelector('#record').dataset.recordId,businessClicks:window.businessClicks,
        settingsClicks:window.settingsClicks,bursts:window.bursts,lastClear:window.lastClear,
        canvasPresent:!!canvas,alpha:canvas?.getContext('2d').getImageData(20,20,1,1).data[3],
        chartAlpha:document.querySelector('#business-chart').getContext('2d').getImageData(0,0,1,1).data[3]};
    });
    assert.equal(state.query,'EXACT-CUSTOMER');assert.equal(state.category,'company');assert.equal(state.record,'121');
    assert.equal(state.businessClicks,0);assert.equal(state.chartAlpha,255);
    assert.equal(state.settingsClicks,mode==='guide-remains'?0:1);
    if(mode==='normal'){
      assert.equal(state.bursts,2);assert(state.canvasPresent);assert.equal(state.alpha,0);
      assert(Date.now()-state.lastClear>=2000,'Wait for natural completion and a full quiet interval');
    }
    if(mode==='persistent'){assert(state.canvasPresent);assert.equal(state.alpha,255)}
    console.log('Native screenshot readiness verified: '+mode);
  }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(error=>{console.error(error);server.close();process.exitCode=1});
"""


@pytest.mark.parametrize("mode", ["normal", "no-canvas", "persistent", "guide-remains"])
def test_screenshot_waits_for_native_decorations_without_masking_business(tmp_path, mode):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual Playwright is required in Actions")
    result = subprocess.run(
        [shutil.which("node"), "-e", DRIVER, mode, module, str(tmp_path / "capture.png")],
        cwd=ROOT,
        env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_decoration_controls_and_query_capture_match_pinned_native_source():
    with zipfile.ZipFile(ROOT / "templates/vendor/fastapiadmin.zip") as archive:
        prefix = "frontend/web/src/"
        header = archive.read(prefix + "layouts/fa-header-bar/index.vue").decode("utf-8")
        drawer = archive.read(
            prefix + "layouts/fa-settings-panel/widgets/FaSettingDrawer.vue"
        ).decode("utf-8")
        effect = archive.read(prefix + "layouts/fa-fireworks-effect/index.vue").decode("utf-8")
        festival = archive.read(prefix + "config/modules/festival.builtin.ts").decode("utf-8")
    assert 'class="setting-btn" @click="openSetting"' in header
    assert "settingStore.hideSettingGuide();" in header
    assert 'modal-class="setting-modal"' in drawer
    assert "close-on-press-escape" not in drawer
    assert 'class="fixed top-0 left-0 z-9999 w-full h-full pointer-events-none"' in effect
    assert "ctx.value.clearRect(0, 0, this.canvasWidth, this.canvasHeight)" in effect
    assert 'name: "国庆节"' in festival and "fireworkInterval: 850" in festival
    source = (ROOT / "scripts/business_fastapi_browser.cjs").read_text(encoding="utf-8")
    query_capture = source.split("report.query_journey =", 1)[1].split("report.checks.push", 1)[0]
    assert "await capture(page, 'manager-customers-native-query-positive')" in query_capture
    assert ".screenshot(" not in query_capture
    assert "await dismissNativeThemeGuide(p)" in source
    assert "getImageData" in source and "canvas.remove" not in source
