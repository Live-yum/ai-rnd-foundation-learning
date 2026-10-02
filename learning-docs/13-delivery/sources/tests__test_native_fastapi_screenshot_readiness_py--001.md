# tests/test_native_fastapi_screenshot_readiness.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_screenshot_waits_for_native_decorations_without_masking_business`（L94–L108）：接收`tmp_path`、`mode`。 控制顺序：L96按`not module or not Path(module).is_dir()`分支；L108断言`result.returncode == 0`。 调用`os.getenv`、`Path(module).is_dir`、`Path`、`pytest.skip`、`subprocess.run`、`shutil.which`、`str`、`clean_env`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_decoration_controls_and_query_capture_match_pinned_native_source`（L111–L132）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L120断言`'class="setting-btn" @click="openSetting"' in header`；L121断言`"settingStore.hideSettingGuide();" in header`；L122断言`'modal-class="setting-modal"' in drawer`；L123断言`"close-on-press-escape" not in drawer`；L124断言`'class="fixed top-0 left-0 z-9999 w-full h-full pointer-events-none"' in effect`；L125断言`"ctx.value.clearRect(0, 0, this.canvasWidth, this.canvasHeight)" in effect`；L126断言`'name: "国庆节"' in festival and "fireworkInterval: 850" in festival`；L129断言`"await capture(page, 'manager-customers-native-query-positive')" in query_capture`。后续分支沿下方源码相同行号继续阅读。 调用`zipfile.ZipFile`、`archive.read(prefix + "layouts/fa-header-bar/index.vue").decode`、`archive.read`、`archive.read( prefix + "layouts/fa-settings-panel/widgets/FaSetti…`、`archive.read(prefix + "layouts/fa-fireworks-effect/index.vue").de…`、`archive.read(prefix + "config/modules/festival.builtin.ts").decod…`、`(ROOT / "scripts/business_fastapi_browser.cjs").read_text`、`source.split("report.query_journey =", 1)[1].split`、`source.split`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_fastapi_screenshot_readiness.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L132。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7584`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_fastapi_screenshot_readiness.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9d63ffc3b2a94330ce054d92f602526b3004acb5785dfbd97d71c120befc3ab6"} -->
````python
# tests/test_native_fastapi_screenshot_readiness.py
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
````
