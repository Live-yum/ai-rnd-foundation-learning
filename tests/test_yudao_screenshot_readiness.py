"""Real Chromium capture semantics; these fixtures are not native-stack receipts."""

import os
from pathlib import Path

import pytest
import test_yudao_navigation_browser as harness

DRIVER = r"""
const assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path'), http=require('node:http');
const {captureNativeScreenshot,nativeScreenshotState}=require('./scripts/business_yudao_browser.cjs');
const [mode,directory,modulePath]=process.argv.slice(1), {chromium}=require(modulePath);
const timers=new Set();
const server=http.createServer((req,res)=>{
 if(req.url==='/slow-font'){
  const timer=setTimeout(()=>{timers.delete(timer);res.writeHead(404);res.end();},8000);
  timers.add(timer);req.on('close',()=>{clearTimeout(timer);timers.delete(timer);});return;
 }
 if(req.url==='/missing-font'){res.writeHead(404);res.end();return;}
 res.writeHead(200,{'Content-Type':'text/html;charset=utf-8'});
 const font=mode==='missing-visible-font'?'/missing-font':'/slow-font';
 res.end(`<style>@font-face{font-family:CaptureProbe;src:url('${font}')}body{font-family:Arial,sans-serif;background:white;color:black}#record{margin:30px;padding:10px}</style>
 ${mode==='blank-business'?'':`<main id="record">Fixture customer title 123<input id="field" value="Private control value"><div id="hidden" style="display:none;font-family:CaptureProbe">Hidden text</div></main>`}
 <script>
 if(${JSON.stringify(mode)}.includes('font')){
  if(${JSON.stringify(mode)}==='pending-control-font')document.querySelector('#field').style.fontFamily='CaptureProbe,Arial';
  else if(${JSON.stringify(mode)}!=='nonvisible-font')document.querySelector('#record').style.fontFamily='CaptureProbe,Arial';
  document.fonts.load('16px CaptureProbe').catch(()=>{});
 }
 if(${JSON.stringify(mode)}==='moving-layout'){
  window.ticks=0;setInterval(()=>{document.querySelector('#record').style.transform='translateX('+(++window.ticks)+'px)';},10);
 }
 </script>`);
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,timeout:8000});
 try{
  const page=await browser.newPage({viewport:{width:700,height:400}});page.setDefaultTimeout(3000);
  await page.goto('http://127.0.0.1:'+server.address().port,{waitUntil:'domcontentloaded'});
  if(mode.includes('font'))await page.waitForFunction(()=>[...document.fonts].some(font=>font.status==='loading'||font.status==='error'));
  if(mode==='missing-visible-font')await page.waitForFunction(()=>[...document.fonts].some(font=>font.status==='error'));
  if(mode!=='blank-business')await page.locator('#field').focus();
  const before=await page.evaluate(()=>({html:document.body.innerHTML,focus:document.activeElement.id}));
  const file=path.join(directory,'capture.png');
  if(mode==='normal'||mode==='nonvisible-font'){
   if(mode==='nonvisible-font'){
    assert.equal(await page.evaluate(()=>document.fonts.status),'loading');
    assert((await nativeScreenshotState(page)).ready);
   }
   await captureNativeScreenshot(page,file,50,1500);
   const bytes=fs.readFileSync(file);assert.equal(bytes.subarray(1,4).toString(),'PNG');
   assert(bytes.length>1000);assert.equal(bytes.readUInt32BE(16),700);assert.equal(bytes.readUInt32BE(20),400);
   assert.deepEqual(await page.evaluate(()=>({html:document.body.innerHTML,focus:document.activeElement.id})),before,'Capture must not change application DOM or focus');
   if(mode==='nonvisible-font')assert.equal(await page.evaluate(()=>document.fonts.status),'loading','Unused pending font must remain unmodified');
  }else{
   await assert.rejects(captureNativeScreenshot(page,file,50,650),/Native screenshot visible-fonts-and-layout did not become ready/);
   assert(!fs.existsSync(file),'Unreadable/unstable/blank page must not produce a success image');
   const diagnostic=JSON.parse(fs.readFileSync(file+'.capture.json','utf8'));
   assert.equal(diagnostic.phase,'visible-fonts-and-layout');
   assert(!JSON.stringify(diagnostic).includes('Fixture customer title'));
   assert(!JSON.stringify(diagnostic).includes('Private control value'));
   if(mode.includes('font'))assert(diagnostic.visible_fonts.some(font=>font.loaded===false),'Visible missing font must remain a strict failure');
   if(mode==='blank-business')assert.equal(diagnostic.visible_text_nodes,0);
   if(mode==='moving-layout')assert(await page.evaluate(()=>window.ticks)>10,'Capture must not stop the app animation to hide layout drift');
  }
  console.log('Real Chromium screenshot readiness fixture PASS '+mode);
 }finally{
  await browser.close();for(const timer of timers)clearTimeout(timer);
  await new Promise(resolve=>{server.close(resolve);server.closeAllConnections();});
 }
})().catch(error=>{console.error(error);process.exitCode=1;});
"""


@pytest.mark.parametrize(
    "mode",
    [
        "normal",
        "nonvisible-font",
        "pending-visible-font",
        "pending-control-font",
        "missing-visible-font",
        "moving-layout",
        "blank-business",
    ],
)
def test_native_pixels_require_visible_fonts_and_stable_business_content(
    tmp_path, monkeypatch, mode
):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual pinned Playwright/Chromium required")
    # Reuse the already-tested, bounded owned-process runner, not pipe-only teardown.
    monkeypatch.setattr(harness, "DRIVER", DRIVER)
    harness._run_driver(mode, str(tmp_path), module)
