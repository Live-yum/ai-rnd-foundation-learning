# tests/test_yudao_screenshot_readiness.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_native_pixels_require_visible_fonts_and_stable_business_content`（L189–L197）：接收`tmp_path`、`monkeypatch`、`mode`。 控制顺序：L193按`not module or not Path(module).is_dir()`分支。 调用`os.getenv`、`Path(module).is_dir`、`Path`、`pytest.skip`、`monkeypatch.setattr`、`harness._run_driver`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_yudao_screenshot_readiness.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L197。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12774`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_yudao_screenshot_readiness.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9004c0ad77f87cd85c95040ab7575fc07cf0bf4c30fd5a07a921ae8081f3abcd"} -->
````python
# tests/test_yudao_screenshot_readiness.py
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
 res.end(`<style>@font-face{font-family:CaptureProbe;src:url('${font}');${mode==='pending-unicode-range'?'unicode-range:U+20BB7;':''}}body{font-family:Arial,sans-serif;background:white;color:black}#record{margin:30px;padding:10px}</style>
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
 if(${JSON.stringify(mode)}==='responsive-layout'){
  const panel=document.querySelector('#record');panel.style='position:absolute;left:30px;right:30px;top:30px;bottom:30px;margin:0';
  window.resizeEvents=[];
  window.addEventListener('resize',()=>resizeEvents.push(['viewport',innerWidth,innerHeight]));
  new ResizeObserver(()=>{const box=panel.getBoundingClientRect();resizeEvents.push(['panel',box.width,box.height]);}).observe(panel);
 }
 if(${JSON.stringify(mode)}==='scrolled-long-page'){
  document.body.style.margin='0';document.body.style.height='1250px';document.body.style.display='flow-root';
  const tail=document.createElement('div');tail.id='tail';tail.style='position:absolute;top:1200px;left:0;width:100%;height:50px;background:rgb(255,0,255)';
  tail.textContent='Full document bottom must remain in the PNG';document.body.append(tail);
 }
 if(${JSON.stringify(mode)}==='batched-unicode'){
  for(let i=0;i<50;i++){
   const text=document.createElement('span');text.style.fontSize='8px';text.textContent='Repeated sample '+i+' 𠮷 Ω';document.querySelector('#record').append(text);
  }
  const control=document.createElement('input');control.value='Unique control Ж';document.querySelector('#record').append(control);
  window.fontCalls=[];const originalCheck=document.fonts.check.bind(document.fonts);
  document.fonts.check=(font,text)=>{fontCalls.push({font,text});return originalCheck(font,text);};
 }
 if(${JSON.stringify(mode)}==='pending-unicode-range'){
  document.querySelector('#record').style.fontFamily='CaptureProbe,Arial';
  const text=document.createElement('span');text.textContent='𠮷';document.querySelector('#record').append(text);
  document.fonts.load('16px CaptureProbe','𠮷').catch(()=>{});
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
  if((mode.includes('font')&&mode!=='capture-visible-font')||mode==='pending-unicode-range')await page.waitForFunction(()=>[...document.fonts].some(font=>font.status==='loading'||font.status==='error'));
  if(mode==='missing-visible-font')await page.waitForFunction(()=>[...document.fonts].some(font=>font.status==='error'));
  if(mode!=='blank-business')await page.locator('#field').focus();
  if(mode==='responsive-layout'){
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   await page.evaluate(()=>resizeEvents.length=0);
  }
  if(mode==='scrolled-long-page')await page.evaluate(()=>window.scrollTo(0,300));
  const originalScroll=await page.evaluate(()=>[scrollX,scrollY]);
  const before=await page.evaluate(()=>({html:document.body.innerHTML,focus:document.activeElement.id}));
  const file=path.join(directory,'capture.png');
  let captures=0, lastPixels, beyond;
  const context=page.context(), originalSession=context.newCDPSession.bind(context);
  context.newCDPSession=async(...args)=>{
   const session=await originalSession(...args), send=session.send.bind(session);
   session.send=async(name,args)=>{
    if(name==='Page.captureScreenshot'){
     beyond=args.captureBeyondViewport;
     captures++;await page.evaluate(()=>window.dispatchEvent(new Event('captureBoundary')));
     const result=await send(name,args);lastPixels=result.data;return result;
    }
    return send(name,args);
   };return session;
  };
  if(['normal','nonvisible-font','late-tooltip','refreshing-text','responsive-layout','scrolled-long-page','batched-unicode'].includes(mode)){
   if(mode==='batched-unicode'){
    const state=await nativeScreenshotState(page);assert(state.ready);
    const checks=await page.evaluate(()=>fontCalls);
    assert.equal(checks.length,new Set(checks.map(check=>check.font)).size,'One actual FontFaceSet check per CSS font per sample, never per element');
    const glyphs=checks.map(check=>check.text).join('');
    for(const glyph of ['𠮷','Ω','Ж','0','9'])assert(glyphs.includes(glyph),'Batch must retain every visible text/control codepoint');
   }
   if(mode==='nonvisible-font'){
    assert.equal(await page.evaluate(()=>document.fonts.status),'loading');
    assert((await nativeScreenshotState(page)).ready);
   }
   const timing=await captureNativeScreenshot(page,file,50,1500);
   for(const key of ['notice_ms','sampling_ms','pixels_ms','samples','duration_ms','capture_attempts'])assert(Number.isInteger(timing[key])&&timing[key]>=0);
   assert(!JSON.stringify(timing).includes('Private control value'));
   const bytes=fs.readFileSync(file);assert.equal(bytes.subarray(1,4).toString(),'PNG');
   assert(bytes.length>1000);assert.equal(bytes.readUInt32BE(16),700);assert.equal(bytes.readUInt32BE(20),mode==='scrolled-long-page'?1250:400);
   assert.equal(beyond,mode==='scrolled-long-page','Only documents exceeding the viewport may request the resize-inducing full-page path');
   assert.deepEqual(await page.evaluate(()=>[scrollX,scrollY]),originalScroll,'Full-document capture must restore the original visible scroll position');
   if(mode==='responsive-layout')assert.deepEqual(await page.evaluate(()=>resizeEvents),[],'A fitting responsive table must never collapse through a screenshot-induced 1x1 viewport');
   if(mode==='scrolled-long-page'){
    const color=await page.evaluate(async data=>{
     const image=new Image();image.src='data:image/png;base64,'+data;await image.decode();
     const canvas=new OffscreenCanvas(image.width,image.height),context=canvas.getContext('2d');context.drawImage(image,0,0);
     return [...context.getImageData(650,1225,1,1).data];
    },bytes.toString('base64'));
    assert.deepEqual(color,[255,0,255,255],'Preserve actual offscreen bottom pixels, not a viewport crop or blank padding');
   }
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
   if(mode.includes('font')||mode==='pending-unicode-range')assert(diagnostic.visible_fonts.some(font=>font.loaded===false),'Visible missing font must remain a strict failure');
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
        "responsive-layout",
        "scrolled-long-page",
        "batched-unicode",
        "pending-unicode-range",
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
````
