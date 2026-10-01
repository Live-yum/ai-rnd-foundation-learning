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
 ${mode==='blank-business'?'':`<main id="record">Fixture customer title 123<input id="field" value="Private control value"><span id="clock" style="font-family:monospace">111</span><div id="hidden" style="display:none;font-family:CaptureProbe">Hidden text</div></main>`}
 <script>
 if(${JSON.stringify(mode)}.includes('font')&&${JSON.stringify(mode)}!=='capture-visible-font'){
  if(${JSON.stringify(mode)}==='pending-control-font')document.querySelector('#field').style.fontFamily='CaptureProbe,Arial';
  else if(${JSON.stringify(mode)}!=='nonvisible-font')document.querySelector('#record').style.fontFamily='CaptureProbe,Arial';
  document.fonts.load('16px CaptureProbe').catch(()=>{});
 }
 if(${JSON.stringify(mode)}==='moving-layout'){
  window.ticks=0;setInterval(()=>{document.querySelector('#record').style.transform='translateX('+(++window.ticks)+'px)';},10);
 }
 window.captureTicks=0;
 window.addEventListener('captureBoundary',()=>{
  window.captureTicks++;
  if(${JSON.stringify(mode)}==='late-tooltip'&&window.captureTicks===1){
   const tooltip=document.createElement('div');tooltip.id='tooltip';tooltip.textContent='Delayed native tooltip';
   tooltip.style='position:absolute;top:120px;left:200px;background:#222;color:white';document.body.append(tooltip);
  }
  if(${JSON.stringify(mode)}==='refreshing-text')document.querySelector('#clock').textContent=window.captureTicks%2?'222':'111';
  if(${JSON.stringify(mode)}==='capture-layout-drift')document.querySelector('#record').style.transform='translateX('+window.captureTicks+'px)';
  if(${JSON.stringify(mode)}==='capture-visible-font'){
   document.querySelector('#record').style.fontFamily='CaptureProbe,Arial';document.fonts.load('16px CaptureProbe').catch(()=>{});
  }
 });
 </script>`);
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,timeout:8000});
 try{
  const page=await browser.newPage({viewport:{width:700,height:400}});page.setDefaultTimeout(3000);
  await page.goto('http://127.0.0.1:'+server.address().port,{waitUntil:'domcontentloaded'});
  if(mode.includes('font')&&mode!=='capture-visible-font')await page.waitForFunction(()=>[...document.fonts].some(font=>font.status==='loading'||font.status==='error'));
  if(mode==='missing-visible-font')await page.waitForFunction(()=>[...document.fonts].some(font=>font.status==='error'));
  if(mode!=='blank-business')await page.locator('#field').focus();
  const before=await page.evaluate(()=>({html:document.body.innerHTML,focus:document.activeElement.id}));
  const file=path.join(directory,'capture.png');
  let captures=0, lastPixels;
  const context=page.context(), originalSession=context.newCDPSession.bind(context);
  context.newCDPSession=async(...args)=>{
   const session=await originalSession(...args), send=session.send.bind(session);
   session.send=async(name,args)=>{
    if(name==='Page.captureScreenshot'){
     captures++;await page.evaluate(()=>window.dispatchEvent(new Event('captureBoundary')));
     const result=await send(name,args);lastPixels=result.data;return result;
    }
    return send(name,args);
   };return session;
  };
  if(['normal','nonvisible-font','late-tooltip','refreshing-text'].includes(mode)){
   if(mode==='nonvisible-font'){
    assert.equal(await page.evaluate(()=>document.fonts.status),'loading');
    assert((await nativeScreenshotState(page)).ready);
   }
   await captureNativeScreenshot(page,file,50,1500);
   const bytes=fs.readFileSync(file);assert.equal(bytes.subarray(1,4).toString(),'PNG');
   assert(bytes.length>1000);assert.equal(bytes.readUInt32BE(16),700);assert.equal(bytes.readUInt32BE(20),400);
   assert.equal(bytes.toString('base64'),lastPixels,'Only the final stable native pixels may be written');
   if(mode==='late-tooltip'){
    assert.equal(captures,2,'Discard the first unstable frame and recapture after the native tooltip settles');
    assert(await page.locator('#tooltip').isVisible(),'Capture must not hide the native tooltip');
   }else if(mode==='refreshing-text'){
    // Chromium may settle its initial system-font metrics on first paint. Text
    // changes on EVERY capture, so success proves text alone cannot loop forever.
    assert(captures<=2,'Equal-geometry live text changes are not layout drift');
    assert.equal(await page.locator('#clock').textContent(),captures%2?'222':'111');
   }else assert.deepEqual(await page.evaluate(()=>({html:document.body.innerHTML,focus:document.activeElement.id})),before,'Capture must not change application DOM or focus');
   assert.equal(await page.evaluate(()=>document.activeElement.id),before.focus,'Capture must preserve user focus');
   if(mode==='nonvisible-font')assert.equal(await page.evaluate(()=>document.fonts.status),'loading','Unused pending font must remain unmodified');
  }else{
   const started=Date.now();
   await assert.rejects(captureNativeScreenshot(page,file,50,650),/Native screenshot (visible-fonts-and-layout|native-pixel-capture|post-capture-readiness) did not become ready/);
   assert(Date.now()-started<1500,'Repeated capture must not reset the overall deadline');
   assert(!fs.existsSync(file),'Unreadable/unstable/blank page must not produce a success image');
   const diagnostic=JSON.parse(fs.readFileSync(file+'.capture.json','utf8'));
   if(mode!=='capture-layout-drift')assert.equal(diagnostic.phase,'visible-fonts-and-layout');
   assert(!JSON.stringify(diagnostic).includes('Fixture customer title'));
   assert(!JSON.stringify(diagnostic).includes('Private control value'));
   if(mode.includes('font'))assert(diagnostic.visible_fonts.some(font=>font.loaded===false),'Visible missing font must remain a strict failure');
   if(mode==='blank-business')assert.equal(diagnostic.visible_text_nodes,0);
   if(mode==='moving-layout')assert(await page.evaluate(()=>window.ticks)>10,'Capture must not stop the app animation to hide layout drift');
   if(mode==='capture-visible-font')assert.equal(captures,1,'Visible font must become pending during the actual first capture');
   if(mode==='capture-layout-drift'){
    assert(captures>=2);assert(diagnostic.last_capture_changes.layout);
    assert.equal(diagnostic.capture_attempts,captures);
   }
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
        "late-tooltip",
        "refreshing-text",
        "capture-layout-drift",
        "capture-visible-font",
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
