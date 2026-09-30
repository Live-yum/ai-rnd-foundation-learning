// Real browser, real authentication and real generated business routes only.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const [configFile, modulePath] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(configFile, 'utf8'));
(async () => {
  const {chromium} = require(modulePath);
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1100}});
  page.setDefaultTimeout(20000);
  const errors=[], checks=new Set(), business=cfg.spec.business, screenshots=new Map();
  page.on('pageerror', error=>errors.push(error.message));
  const grant=(role,entity)=>business.permissions.find(p=>p.role===role&&p.entity===entity);
  const allowed=(role,entity,action)=>grant(role,entity)?.actions.includes(action);
  async function capture(actor, entity, view) {
    if(!cfg.screenshot_dir)return;
    assert(/^[a-z][a-z0-9_]{0,39}$/.test(actor.role));
    assert(entity===null || /^[a-z][a-z0-9_]{0,39}$/.test(entity));
    assert(['list','form','relations','workflow','reminders','dashboard'].includes(view));
    const file=`${actor.role}--${entity||'overview'}--${view}.png`;
    if(screenshots.has(file))return;
    assert(screenshots.size<48,'Screenshot evidence limit reached');
    assert(await page.locator('#workspace').isVisible());
    assert(await page.locator('#login').isHidden());
    await page.screenshot({path:path.join(cfg.screenshot_dir,file),type:'png',fullPage:true,
      mask:[page.locator('input[type=password]')]});
    screenshots.set(file,{file,role:actor.role,entity,view});
  }
  async function login(actor) {
    if(page.url().startsWith(cfg.url)) await Promise.all([page.waitForEvent('load'),page.locator('#logout').click()]);
    else await page.goto(cfg.url);
    await page.locator('#auth input[name=username]').fill(actor.username);
    await page.locator('#auth input[name=password]').fill('invalid-password-for-verification');
    await page.locator('#auth button[type=submit]').click();
    await page.waitForFunction(()=>document.querySelector('#notice').textContent.length>0);
    assert(await page.locator('#workspace').isHidden());
    await page.locator('#auth input[name=password]').fill(cfg.password);
    await page.locator('#auth button[type=submit]').click();
    await page.locator('#workspace').waitFor({state:'visible'});
    assert((await page.locator('#business-role').innerText()).includes(actor.role));
    checks.add('business-browser-auth');
    const permitted=cfg.spec.entities.filter(e=>allowed(actor.role,e.name,'read'));
    assert.equal(await page.locator('#entities button').count(),permitted.length);
    assert.equal(await page.locator('#business-admin').isVisible(),business.role_admin_roles.includes(actor.role));
    checks.add('business-browser-role-navigation');
    const metrics=business.metrics.filter(m=>allowed(actor.role,m.entity,'read_metrics'));
    assert.equal(await page.locator('#business-metrics section').count(),metrics.length);
    for(const metric of metrics) assert((await page.locator('#business-metrics').innerText()).includes(metric.label));
    if(metrics.length) checks.add('business-browser-metrics');
    await capture(actor,null,'dashboard');
    await capture(actor,null,'reminders');
    const mark=page.locator('#business-notifications button');
    if(await mark.count()) {
      const response=page.waitForResponse(r=>r.url().includes('/business/notifications/')&&r.request().method()==='POST');
      await mark.first().click(); assert.equal((await response).status(),200);
      checks.add('business-browser-reminders');
    }
  }
  async function choose(entity) {
    const response=page.waitForResponse(r=>r.url().includes('/api/'+entity.name+'?')&&r.request().method()==='GET');
    await page.locator('#entities button').filter({hasText:entity.description||entity.name}).click();
    assert.equal((await response).status(),200);
    await page.waitForTimeout(50);
  }
  try {
    for(const entity of cfg.spec.entities) {
      const actor=cfg.actors.find(a=>a.role===cfg.create_roles[entity.name]);
      await login(actor);await choose(entity);
      await capture(actor,entity.name,'list');
      assert(await page.locator('#create').isVisible());
      await page.locator('#create').click();await page.locator('#editor').waitFor({state:'visible'});
      const resource=business.resources.find(r=>r.entity===entity.name);
      const workflow=business.workflows.find(w=>w.entity===entity.name);
      const protectedFields=new Set([resource.assignee_field,workflow?.status_field,...(workflow?.transitions||[]).map(t=>t.set_timestamp)]);
      for(const field of entity.fields) {
        const control=page.locator(`#record [name="${field.name}"]`);
        if(protectedFields.has(field.name)){assert.equal(await control.count(),0);continue;}
        const value=cfg.samples[entity.name][field.name];
        if(value===null||value===undefined)continue;
        const tag=await control.evaluate(node=>node.tagName);
        if(tag==='SELECT')await control.selectOption(String(value));
        else await control.fill(field.kind==='datetime'?String(value).replace(/Z$/,'').slice(0,16):String(value));
      }
      await capture(actor,entity.name,'form');
      const createdResponse=page.waitForResponse(r=>r.url().endsWith('/api/'+entity.name)&&r.request().method()==='POST');
      await page.locator('#record button[type=submit]').click();const created=await createdResponse;
      assert.equal(created.status(),201);let row=await created.json();
      await page.locator('#editor').waitFor({state:'hidden'});
      const line=page.locator(`#rows tr[data-id="${row.id}"]`);await line.waitFor();
      checks.add('business-browser-records:'+entity.name);
      for(const field of entity.fields.filter(f=>f.searchable)) {
        const input=page.locator('#filters [name=q]');await input.fill(String(cfg.samples[entity.name][field.name]));
        const response=page.waitForResponse(r=>r.url().includes('/api/'+entity.name+'?')&&r.request().method()==='GET');
        await page.locator('#filters button[type=submit]').click();assert.equal((await response).status(),200);
        await line.waitFor();await page.locator('#reset').click();await page.waitForTimeout(75);
      }
      for(const field of entity.fields.filter(f=>f.filterable)) {
        if(row[field.name]===null)continue;
        const input=page.locator(`#filters [name="filter_${field.name}"]`);
        const tag=await input.evaluate(node=>node.tagName);
        if(tag==='SELECT')await input.selectOption(String(row[field.name]));else await input.fill(String(row[field.name]));
        const response=page.waitForResponse(r=>r.url().includes('filter_'+field.name+'=')&&r.request().method()==='GET');
        await page.locator('#filters button[type=submit]').click();assert.equal((await response).status(),200);await line.waitFor();
        await page.locator('#reset').click();await page.waitForTimeout(75);
      }
      await line.getByRole('button',{name:'详情 / 处理'}).click();await page.locator('#business-detail').waitFor({state:'visible'});
      if(resource.assignee_field&&allowed(actor.role,entity.name,'assign')) {
        const target=cfg.actors.find(a=>grant(a.role,entity.name)?.scope==='assigned'&&allowed(a.role,entity.name,'read')&&(allowed(a.role,entity.name,'update')||allowed(a.role,entity.name,'transition')))||actor;
        await page.locator('#business-assignee').selectOption(target.id);
        const response=page.waitForResponse(r=>r.url().endsWith('/assign')&&r.request().method()==='POST');
        await page.locator('#business-actions').getByRole('button',{name:'分配',exact:true}).click();const assigned=await response;assert.equal(assigned.status(),200);row=await assigned.json();
        checks.add('business-browser-assignment');await page.waitForTimeout(100);
      }
      if(resource.notes&&allowed(actor.role,entity.name,'add_note')) {
        await page.locator('#business-note-form textarea').fill('Browser business acceptance note');
        const response=page.waitForResponse(r=>r.url().endsWith('/notes')&&r.request().method()==='POST');
        await page.locator('#business-note-form button').click();assert.equal((await response).status(),201);
        await page.locator('#business-notes').getByText(/Browser business acceptance note/).waitFor();
        await page.locator('#business-history').getByText(/note_added/).waitFor();
        checks.add('business-browser-notes-history');
      }
      if(workflow)await capture(actor,entity.name,'workflow');
      const visited=new Set();
      while(workflow&&!visited.has(row[workflow.status_field])) {
        visited.add(row[workflow.status_field]);
        const operation=workflow.transitions.find(t=>t.roles.includes(actor.role)&&t.from_states.includes(row[workflow.status_field]));
        if(!operation)break;
        const button=page.locator('#business-actions').getByRole('button',{name:operation.name,exact:true});await button.waitFor();
        const response=page.waitForResponse(r=>r.url().endsWith('/transition')&&r.request().method()==='POST');
        await button.click();const transition=await response;assert.equal(transition.status(),200);row=await transition.json();
        assert.equal(row[workflow.status_field],operation.to_state);checks.add('business-browser-transitions');await page.waitForTimeout(100);
      }
      await page.locator('#business-close').click();
    }
    for(const actor of cfg.actors) {
      await login(actor);
      for(const entity of cfg.spec.entities.filter(e=>allowed(actor.role,e.name,'read'))) {
        await choose(entity);assert.equal(await page.locator('#create').isVisible(),!!allowed(actor.role,entity.name,'create'));
        const line=page.locator('#rows tr').first();
        if(await line.count()) {
          assert.equal(await line.getByRole('button',{name:'编辑',exact:true}).count()>0,!!allowed(actor.role,entity.name,'update'));
          assert.equal(await line.getByRole('button',{name:'归档',exact:true}).count()>0,!!allowed(actor.role,entity.name,'archive'));
        }
        await capture(actor,entity.name,'list');
        if(cfg.screenshot_dir) {
          if(allowed(actor.role,entity.name,'create')) {
            await page.locator('#create').click();await page.locator('#editor').waitFor({state:'visible'});
            await capture(actor,entity.name,'form');await page.locator('#cancel').click();
          } else if(await line.count() && allowed(actor.role,entity.name,'update')) {
            await line.getByRole('button',{name:'编辑',exact:true}).click();await page.locator('#editor').waitFor({state:'visible'});
            await capture(actor,entity.name,'form');await page.locator('#cancel').click();
          }
          let detail=page.locator(`#rows tr[data-id="${cfg.base_records?.[entity.name]||''}"]`);
          if(!(await detail.count()))detail=line;
          if(await detail.count()) {
            await detail.getByRole('button',{name:'详情 / 处理'}).click();await page.locator('#business-detail').waitFor({state:'visible'});
            await capture(actor,entity.name,'relations');
            if(business.workflows.some(w=>w.entity===entity.name))await capture(actor,entity.name,'workflow');
            await page.locator('#business-close').click();
          }
        }
      }
    }
    checks.add('business-browser-role-restrictions');checks.add('business-browser-actions');
    assert.deepEqual(errors,[]);
    fs.writeFileSync(cfg.output,JSON.stringify({passed:true,real_browser:true,entities:cfg.spec.entities.map(e=>e.name),spec_digest:cfg.spec_digest,checks:[...checks],errors,screenshots:[...screenshots.values()]}));
  }finally{await browser.close();}
})().catch(error=>{console.error(error?.name||'BusinessBrowserFailure');process.exitCode=1;});
