# templates/product/verify-business-browser.cjs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** Python轻量原生UI的三角色真实Chromium场景：通过登录、列表、关联表单、详情动作、提醒及统计控件完成客服流程，记录检查项和合成数据截图；不注入token或mock接口。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/product/verify-business-browser.cjs`；**本文件共有 1 段**。本段覆盖源文件 L1–L481。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`37336`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/verify-business-browser.cjs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3929f9ca88f38a6165fe53ca733acfa9dd0c0234734a58835a9fe8dc8ab51432"} -->
````javascript
// templates/product/verify-business-browser.cjs
// Real browser, real authentication and real generated business routes only.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
function browserFailure(error) {
  // Retain the failing static operation/callsite, never Playwright's raw DOM,
  // URLs, credentials, values, absolute paths or complete error/stack text.
  const message=String(error?.message||'');
  const code=/^business-browser-[a-z0-9-]{1,100}$/.test(message)?message:
    /^[A-Za-z]{1,40}Error$/.test(error?.name||'')?error.name:'BusinessBrowserFailure';
  const operation=message.match(/^(locator\.(?:click|fill|waitFor|selectOption|evaluate|evaluateAll|innerText|inputValue)|page\.(?:goto|waitForURL|waitForFunction|waitForResponse|waitForEvent|waitForLoadState|screenshot)):/)?.[1]||null;
  const callsites=[...String(error?.stack||'').matchAll(/(?:^|[\\/])verify-business-browser\.cjs:(\d{1,6}):(\d{1,6})(?=[)\s]|$)/gm)]
    .slice(0,5).map(match=>({line:Number(match[1]),column:Number(match[2])}));
  return code+' '+JSON.stringify({source:'verify-business-browser.cjs',operation,callsites});
}
module.exports={browserFailure};
if(require.main===module) {
const [configFile, modulePath] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(configFile, 'utf8'));
(async () => {
  const {chromium} = require(modulePath);
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1100}});
  page.setDefaultTimeout(20000);
  const errors=[], checks=new Set(), business=cfg.spec.business, screenshots=new Map();
  // These summaries contain only approved contract names, booleans and bounded counts.
  // Expected identities and display values stay in this isolated verifier process.
  const evidence={version:1,relation_labels:[],related_views:[],related_sources:[],datetime_controls:[],query_matrix:[]};
  const labelEvidence=new Map(), relatedEvidence=new Map(), sourceEvidence=new Map();
  const entities=new Map(cfg.spec.entities.map(entity=>[entity.name,entity]));
  const roles=new Set(business.roles.map(role=>role.name));
  const limit=100;
  const verify=(condition,code)=>assert(condition,'business-browser-'+code);
  const rowSelector=id=>`#rows tr[data-id=${JSON.stringify(String(id))}]`;
  const tuple=(...parts)=>JSON.stringify(parts);
  const summary=(map,key,initial)=>{if(!map.has(key))map.set(key,initial);return map.get(key);};
  const relationFor=(entity,field)=>business.relations.find(r=>r.entity===entity&&r.field===field);
  const queryKey=item=>tuple(item.role,item.entity,item.field,item.kind);
  function validateQueryExpectations() {
    verify(Array.isArray(cfg.query_cases)&&Array.isArray(cfg.query_evidence),'query-expectations-missing');
    const required=new Map();
    for(const actor of cfg.actors)for(const entity of cfg.spec.entities.filter(entity=>allowed(actor.role,entity.name,'read'))) {
      const keyword=entity.fields.find(field=>field.searchable);
      for(const field of entity.fields) {
        const kinds=[...(field.searchable?['keyword']:[]),...(field.filterable?['exact_filter',...(keyword?['combined']:[])]:[])];
        for(const kind of kinds) {
          const item={role:actor.role,entity:entity.name,field:field.name,kind,keyword_field:kind==='combined'?keyword.name:null};
          required.set(queryKey(item),item);
        }
      }
    }
    verify(cfg.query_cases.length===required.size*2&&cfg.query_evidence.length===required.size,'query-expectations-coverage');
    const pairs=new Map();
    for(const item of cfg.query_cases) {
      const expected=required.get(queryKey(item));
      verify(!!expected&&item.keyword_field===expected.keyword_field,'query-expectations-scope');
      const variants=item.kind==='keyword'?['match','miss']:['match','other'];
      verify(variants.includes(item.variant),'query-expectations-variant');
      verify(item.params&&typeof item.params==='object'&&!Array.isArray(item.params),'query-expectations-params');
      const names=item.kind==='keyword'?['q']:item.kind==='exact_filter'?['filter_'+item.field]:['filter_'+item.field,'q'];
      verify(JSON.stringify(Object.keys(item.params).sort())===JSON.stringify(names.sort())&&Object.values(item.params).every(value=>typeof value==='string'&&value.length>0&&value.length<=4096),'query-expectations-params');
      verify(Array.isArray(item.expected_ids)&&item.expected_ids.length<=50&&item.expected_ids.every(id=>typeof id==='string'&&!!id)&&new Set(item.expected_ids).size===item.expected_ids.length,'query-expectations-identities');
      verify(Number.isInteger(item.total_count)&&item.total_count>=item.expected_ids.length&&item.total_count<=limit,'query-expectations-count');
      for(const name of ['foreign_count','isolated_count'])verify(Number.isInteger(item[name])&&item[name]>=0&&item[name]<=limit,'query-expectations-count');
      verify(item.isolated_count<=item.expected_ids.length&&(item.kind==='keyword'||item.isolated_count===0),'query-expectations-isolation');
      if(item.variant==='miss')verify(item.expected_ids.length===0,'query-expectations-miss');
      const pair=summary(pairs,queryKey(item),[]);
      verify(!pair.some(other=>other.variant===item.variant),'query-expectations-duplicate');pair.push(item);
    }
    const seen=new Set();
    for(const entry of cfg.query_evidence) {
      const key=queryKey(entry),expected=required.get(key),pair=pairs.get(key);
      verify(!!expected&&!seen.has(key)&&pair?.length===2,'query-evidence-coverage');seen.add(key);
      verify(entry.keyword_field===expected.keyword_field&&entry.scope===grant(entry.role,entry.entity)?.scope,'query-evidence-scope');
      verify(entry.cases===2&&entry.exact_results===true&&entry.role_scope===true,'query-evidence-result');
      for(const name of ['positive_matches','other_matches','excluded_records','foreign_matches','isolated_matches'])verify(Number.isInteger(entry[name])&&entry[name]>=0&&entry[name]<=limit*2,'query-evidence-count');
      verify(entry.positive_matches===pair.find(item=>item.variant==='match').expected_ids.length&&entry.other_matches===pair.find(item=>item.variant!=='match').expected_ids.length,'query-evidence-matches');
      verify(entry.excluded_records===pair.reduce((count,item)=>count+item.total_count-item.expected_ids.length,0)&&entry.foreign_matches===pair.reduce((count,item)=>count+item.foreign_count,0)&&entry.isolated_matches===pair.reduce((count,item)=>count+item.isolated_count,0),'query-evidence-counts');
    }
    for(const entity of cfg.spec.entities)for(const field of entity.fields.filter(field=>field.searchable))verify(cfg.query_evidence.some(entry=>entry.entity===entity.name&&entry.field===field.name&&entry.kind==='keyword'&&entry.isolated_matches>0),'query-field-isolation');
  }
  function validateExpectations() {
    validateQueryExpectations();
    verify(Array.isArray(cfg.relation_labels),'label-expectations-missing');
    verify(Array.isArray(cfg.related_expectations),'related-expectations-missing');
    verify(cfg.relation_labels.length<=roles.size*business.relations.length*limit,'label-expectations-limit');
    verify(cfg.related_expectations.length<=roles.size*entities.size*limit,'related-expectations-limit');
    const labels=new Set(),sources=new Set(),labelCounts=new Map(),sourceCounts=new Map();
    for(const item of cfg.relation_labels) {
      verify(roles.has(item.role)&&entities.has(item.entity)&&allowed(item.role,item.entity,'read'),'label-expectations-scope');
      verify(!!relationFor(item.entity,item.field),'label-expectations-relation');
      verify(typeof item.record_id==='string'&&typeof item.target_id==='string','label-expectations-identity');
      verify(typeof item.visible==='boolean'&&(item.visible?typeof item.label==='string'&&!!item.label:item.label===null),'label-expectations-value');
      const key=tuple(item.role,item.entity,item.record_id,item.field);
      verify(!labels.has(key),'label-expectations-duplicate');labels.add(key);
      const countKey=tuple(item.role,item.entity,item.field);
      labelCounts.set(countKey,(labelCounts.get(countKey)||0)+1);
      verify(labelCounts.get(countKey)<=limit,'label-expectations-field-limit');
    }
    for(const item of cfg.related_expectations) {
      verify(roles.has(item.role)&&entities.has(item.entity)&&allowed(item.role,item.entity,'read'),'related-expectations-scope');
      verify(typeof item.record_id==='string'&&Array.isArray(item.groups),'related-expectations-value');
      const key=tuple(item.role,item.entity,item.record_id);
      verify(!sources.has(key),'related-expectations-duplicate');sources.add(key);
      const countKey=tuple(item.role,item.entity);
      sourceCounts.set(countKey,(sourceCounts.get(countKey)||0)+1);
      verify(sourceCounts.get(countKey)<=limit,'related-expectations-source-limit');
      const expected=business.relations.filter(r=>r.target_entity===item.entity&&allowed(item.role,r.entity,'read'));
      verify(item.groups.length===expected.length,'related-expectations-groups');
      const groups=new Set();
      for(const group of item.groups) {
        const relation=expected.find(r=>r.entity===group.entity&&r.field===group.field);
        verify(!!relation&&!groups.has(tuple(group.entity,group.field)),'related-expectations-relation');
        groups.add(tuple(group.entity,group.field));
        verify(Array.isArray(group.record_ids)&&Array.isArray(group.labels)&&group.record_ids.length===group.labels.length&&group.record_ids.length<=limit,'related-expectations-records');
        verify(new Set(group.record_ids).size===group.record_ids.length&&group.record_ids.every(id=>typeof id==='string')&&group.labels.every(label=>typeof label==='string'&&!!label),'related-expectations-labels');
      }
    }
    verify(cfg.relation_labels.every(item=>sources.has(tuple(item.role,item.entity,item.record_id))),'label-expectations-source');
  }
  async function verifyFilterControls(actor,entity) {
    const actual=await page.locator('#filters input[name],#filters select[name],#filters textarea[name]').evaluateAll(nodes=>nodes.map(node=>node.name).sort());
    const expected=entity.fields.some(field=>field.searchable)?['q']:[];
    for(const field of entity.fields) {
      if(field.filterable)expected.push('filter_'+field.name);
      if(field.date_range)expected.push('from_'+field.name,'to_'+field.name);
    }
    verify(JSON.stringify(actual)===JSON.stringify(expected.sort()),'filter-controls-contract');
    for(const field of entity.fields.filter(field=>field.kind==='datetime')) {
      evidence.datetime_controls.push({role:actor.role,entity:entity.name,field:field.name,searchable:!!field.searchable,date_range:!!field.date_range,filterable:!!field.filterable,controls_absent:!field.searchable&&!field.date_range&&!field.filterable});
    }
    checks.add('business-browser-datetime-controls');
  }
  function verifyQueryValues(response,params) {
    const query=new URL(response.url()).searchParams;
    verify(query.getAll('offset').length===1&&query.get('offset')==='0'&&query.getAll('limit').length===1&&query.get('limit')==='50','query-pagination-values');
    const active=[...query.entries()].filter(([name])=>!['offset','limit'].includes(name)).sort(([left],[right])=>left.localeCompare(right));
    const expected=Object.entries(params).sort(([left],[right])=>left.localeCompare(right));
    verify(JSON.stringify(active)===JSON.stringify(expected),'query-control-values');
  }
  async function verifyQueryResults(response,entity,expectedIds) {
    verify(response.status()===200,'query-http-status');
    const rows=await response.json();
    verify(Array.isArray(rows)&&rows.length<=limit&&rows.every(row=>row&&typeof row.id==='string'),'query-response-shape');
    const expected=[...expectedIds].sort();
    verify(JSON.stringify(rows.map(row=>row.id).sort())===JSON.stringify(expected),'query-response-ids');
    verify(response.headers()['x-total-count']===String(expected.length),'query-response-total');
    await page.waitForFunction(name=>document.querySelector('#rows').dataset.entity===name&&document.querySelector('#rows').dataset.loading==='false',entity.name);
    const rendered=await page.locator('#rows tr').evaluateAll(nodes=>nodes.map(node=>node.dataset.id).sort());
    verify(JSON.stringify(rendered)===JSON.stringify(expected),'query-rendered-ids');
    return rows;
  }
  async function verifyQueries(actor,entity,sources) {
    const cases=cfg.query_cases.filter(item=>item.role===actor.role&&item.entity===entity.name);
    const listResponse=()=>page.waitForResponse(response=>new URL(response.url()).pathname===`/api/${entity.name}`&&response.request().method()==='GET');
    for(const item of cases) {
      verify(item.total_count===sources.length,'query-source-count');
      const controls=page.locator('#filters input[name],#filters select[name],#filters textarea[name]');
      verify(await controls.evaluateAll(nodes=>nodes.every(node=>node.value==='')),'query-controls-reset');
      for(const [name,value] of Object.entries(item.params)) {
        const control=page.locator(`#filters [name=${JSON.stringify(name)}]`);
        verify(await control.count()===1,'query-control-present');
        if(await control.evaluate(node=>node.tagName)==='SELECT')await control.selectOption(value);
        else await control.fill(value);
        verify(await control.inputValue()===value,'query-control-input');
      }
      const pending=listResponse();
      await page.locator('#filters button[type=submit]').click();
      const response=await pending;verifyQueryValues(response,item.params);
      const rows=await verifyQueryResults(response,entity,item.expected_ids);
      if(item.kind==='keyword'&&item.variant==='match') {
        const term=item.params.q.toLowerCase();
        const matches=(row,field)=>String(row[field]??'').toLowerCase().includes(term);
        const isolated=rows.filter(row=>matches(row,item.field)&&!entity.fields.some(field=>field.searchable&&field.name!==item.field&&matches(row,field.name))).length;
        verify(isolated===item.isolated_count,'query-field-isolation');
      }
      const clearing=listResponse();
      await page.locator('#reset').click();
      const cleared=await clearing;verifyQueryValues(cleared,{});
      verify(await controls.evaluateAll(nodes=>nodes.every(node=>node.value==='')),'query-controls-reset');
      await verifyQueryResults(cleared,entity,sources.map(item=>item.record_id));
    }
    for(const entry of cfg.query_evidence.filter(entry=>entry.role===actor.role&&entry.entity===entity.name)) {
      const {role,entity,field,kind,keyword_field,scope,cases,positive_matches,other_matches,excluded_records,foreign_matches,isolated_matches}=entry;
      evidence.query_matrix.push({role,entity,field,kind,keyword_field,scope,cases,positive_matches,other_matches,excluded_records,foreign_matches,isolated_matches,exact_results:true,role_scope:true,query_values_verified:true,response_ids_exact:true,rendered_ids_exact:true,controls_reset:true});
    }
    checks.add('business-browser-query-matrix');
  }
  async function verifyListLabels(actor,entity,expectations) {
    for(const item of expectations) {
      const line=page.locator(rowSelector(item.record_id));
      verify(await line.count()===1,'label-source-visible');
      const index=entity.fields.findIndex(field=>field.name===item.field);
      const cell=line.locator('td').nth(index);
      const label=await cell.innerText();
      verify(label===(item.visible?item.label:'关联记录不可见')&&label!==item.target_id,'relation-list-label');
      verify(await cell.getAttribute('title')===label,'relation-list-title');
      const entry=summary(labelEvidence,tuple(actor.role,entity.name,item.field),{role:actor.role,entity:entity.name,field:item.field,list:true,select:null,detail:null,records_checked:0});
      entry.records_checked++;
    }
  }
  async function verifySelectLabels(actor,entity,expectations) {
    const resource=business.resources.find(resource=>resource.entity===entity.name);
    const workflow=business.workflows.find(workflow=>workflow.entity===entity.name);
    const protectedFields=new Set([resource.assignee_field,workflow?.status_field,...(workflow?.transitions||[]).map(t=>t.set_timestamp)]);
    const applicable=expectations.filter(item=>relationFor(item.entity,item.field).target_entity!=='$users'&&!protectedFields.has(item.field));
    if(!applicable.length||(!allowed(actor.role,entity.name,'create')&&!allowed(actor.role,entity.name,'update')))return;
    if(allowed(actor.role,entity.name,'create'))await page.locator('#create').click();
    else await page.locator(rowSelector(applicable[0].record_id)).getByRole('button',{name:'编辑',exact:true}).click();
    await page.locator('#editor').waitFor({state:'visible'});
    for(const item of applicable) {
      const select=page.locator(`#record select[name="${item.field}"]`);
      verify(await select.count()===1,'relation-select-control');
      const options=await select.locator('option').evaluateAll(nodes=>nodes.map(node=>({value:node.value,label:node.textContent})));
      const option=options.find(option=>option.value===item.target_id);
      const target=entities.get(relationFor(item.entity,item.field).target_entity);
      const hasDisplayField=target.fields.some(field=>['name','title'].includes(field.name));
      const expectedLabel=hasDisplayField?item.label:item.target_id;
      verify(item.visible?!!option&&option.label===expectedLabel&&(!hasDisplayField||option.label!==item.target_id):!option,'relation-select-label');
      labelEvidence.get(tuple(actor.role,entity.name,item.field)).select=true;
    }
    await page.locator('#cancel').click();
  }
  async function openDetail(entity,recordId) {
    const response=page.waitForResponse(r=>new URL(r.url()).pathname===`/business/related/${entity.name}/${recordId}`&&r.request().method()==='GET');
    await page.locator(rowSelector(recordId)).getByRole('button',{name:'详情 / 处理',exact:true}).click();
    const result=await response;verify(result.status()===200,'related-http-status');
    const groups=await result.json();
    await page.locator('#business-detail').waitFor({state:'visible'});
    return groups;
  }
  async function verifyRelated(actor,entity,item,labels) {
    const groups=await openDetail(entity,item.record_id);
    verify(Array.isArray(groups)&&groups.length===item.groups.length,'related-group-count');
    const expectedKeys=item.groups.map(group=>tuple(group.entity,group.field)).sort();
    verify(JSON.stringify(groups.map(group=>tuple(group.entity,group.field)).sort())===JSON.stringify(expectedKeys),'related-group-scope');
    const headers=await page.locator('#business-related h4').allTextContents();
    verify(JSON.stringify(headers.sort())===JSON.stringify(item.groups.map(group=>entities.get(group.entity).description||group.entity).sort()),'related-headings');
    const expectedButtons=[];
    for(const group of item.groups) {
      const actual=groups.find(actual=>actual.entity===group.entity&&actual.field===group.field);
      verify(Array.isArray(actual.records)&&actual.records.length<=limit,'related-records-shape');
      verify(JSON.stringify(actual.records.map(row=>row.id).sort())===JSON.stringify([...group.record_ids].sort()),'related-target-row-acl');
      const workflow=business.workflows.find(workflow=>workflow.entity===group.entity);
      const stateField=entities.get(group.entity).fields.find(field=>field.name===workflow?.status_field);
      for(let index=0;index<group.record_ids.length;index++) {
        const record=actual.records.find(row=>row.id===group.record_ids[index]);
        const label=group.labels[index];
        const text=label+(workflow?' · '+(stateField?.choice_labels?.[record[workflow.status_field]]||record[workflow.status_field]):'');
        const hasDisplayField=entities.get(group.entity).fields.some(field=>['name','title'].includes(field.name));
        verify(!hasDisplayField||label!==record.id,'related-readable-label');
        expectedButtons.push({text,label,entity:group.entity,recordId:record.id,field:group.field});
      }
      const entry=summary(relatedEvidence,tuple(actor.role,entity.name,group.entity,group.field),{role:actor.role,entity:entity.name,target_entity:group.entity,field:group.field,source_records:0,expected_records:0,visible_records:0,target_acl:true,navigation:null});
      entry.source_records++;entry.expected_records+=group.record_ids.length;entry.visible_records+=actual.records.length;
    }
    const orderedButtons=groups.flatMap(group=>group.records.map(record=>expectedButtons.find(button=>button.entity===group.entity&&button.field===group.field&&button.recordId===record.id)));
    const buttons=await page.locator('#business-related button').allTextContents();
    verify(JSON.stringify(buttons)===JSON.stringify(orderedButtons.map(button=>button.text)),'related-rendered-records');
    verify(await page.locator('#business-related p').count()===item.groups.filter(group=>!group.record_ids.length).length,'related-empty-groups');
    // Notes require history; full audit is an independent approved capability.
    if(!allowed(actor.role,entity.name,'read_history')) {
      verify(await page.locator('#business-notes > *').count()===0,'notes-permission');
    }
    if(!allowed(actor.role,entity.name,'read_history')&&!allowed(actor.role,entity.name,'read_audit')) {
      verify(await page.locator('#business-history > *').count()===0,'history-permission');
    } else {
      verify(await page.locator('#business-history > p').count()>0,'history-visible');
      const auditDetails=await page.locator('#business-history > details').count();
      verify(allowed(actor.role,entity.name,'read_audit')?auditDetails>0:auditDetails===0,'audit-permission');
    }
    const resource=business.resources.find(resource=>resource.entity===entity.name);
    for(const label of labels.filter(label=>label.record_id===item.record_id&&label.field===resource.assignee_field)) {
      if(!allowed(actor.role,entity.name,'assign'))continue;
      const select=page.locator('#business-assignee');
      verify(await select.inputValue()===label.target_id,'assignee-detail-value');
      const text=await select.locator('option:checked').innerText();
      verify(text===label.label&&text!==label.target_id,'assignee-detail-label');
      const entry=labelEvidence.get(tuple(actor.role,entity.name,label.field));entry.select=true;entry.detail=true;
    }
    const source=summary(sourceEvidence,tuple(actor.role,entity.name),{role:actor.role,entity:entity.name,source_records:0,groups_checked:0,target_acl:true});
    source.source_records++;source.groups_checked+=item.groups.length;
    await capture(actor,entity.name,'relations');
    // One real navigation for every nonempty role/relation proves the labelled cards work.
    for(const button of expectedButtons) {
      const entry=relatedEvidence.get(tuple(actor.role,entity.name,button.entity,button.field));
      if(entry.navigation)continue;
      const response=page.waitForResponse(r=>new URL(r.url()).pathname===`/business/related/${button.entity}/${button.recordId}`&&r.request().method()==='GET');
      await page.locator('#business-related button').nth(orderedButtons.indexOf(button)).click();
      verify((await response).status()===200,'related-navigation-status');
      await page.locator('#business-detail').waitFor({state:'visible'});
      verify(await page.locator('#business-detail-title').innerText()===button.label,'related-detail-label');
      await page.waitForFunction(name=>document.querySelector('#rows').dataset.entity===name&&document.querySelector('#rows').dataset.loading==='false',button.entity);
      entry.navigation=true;
      await page.locator('#business-close').click();await choose(entity);await openDetail(entity,item.record_id);
    }
    await page.locator('#business-close').click();
  }
  async function verifySnapshot() {
    validateExpectations();
    for(const actor of cfg.actors) {
      await login(actor);
      for(const entity of cfg.spec.entities.filter(entity=>allowed(actor.role,entity.name,'read'))) {
        await choose(entity);await verifyFilterControls(actor,entity);
        const sources=cfg.related_expectations.filter(item=>item.role===actor.role&&item.entity===entity.name);
        const visibleIds=await page.locator('#rows tr').evaluateAll(nodes=>nodes.map(node=>node.dataset.id).sort());
        verify(JSON.stringify(visibleIds)===JSON.stringify(sources.map(item=>item.record_id).sort()),'source-list-row-acl');
        await verifyQueries(actor,entity,sources);
        const labels=cfg.relation_labels.filter(item=>item.role===actor.role&&item.entity===entity.name);
        await verifyListLabels(actor,entity,labels);await verifySelectLabels(actor,entity,labels);
        for(const item of sources)await verifyRelated(actor,entity,item,labels);
      }
    }
    evidence.relation_labels=[...labelEvidence.values()];evidence.related_views=[...relatedEvidence.values()];evidence.related_sources=[...sourceEvidence.values()];
    verify(evidence.relation_labels.length<=roles.size*business.relations.length&&evidence.related_views.length<=roles.size*business.relations.length&&evidence.related_sources.length<=roles.size*entities.size,'evidence-contract-bound');
    verify(evidence.datetime_controls.length<=roles.size*cfg.spec.entities.reduce((count,entity)=>count+entity.fields.filter(field=>field.kind==='datetime').length,0),'datetime-evidence-bound');
    if(evidence.relation_labels.length)checks.add('business-browser-relation-labels');
    checks.add('business-browser-related-views');checks.add('business-browser-related-row-acl');
  }
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
    await page.screenshot({path:path.join(cfg.screenshot_dir,file),type:'png',fullPage:!['form','relations','workflow'].includes(view),animations:'disabled',
      mask:[page.locator('input[type=password]:visible')]});
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
    assert((await page.locator('#business-role').innerText()).includes(business.roles.find(role=>role.name===actor.role)?.label||actor.role));
    checks.add('business-browser-auth');
    const permitted=cfg.spec.entities.filter(e=>allowed(actor.role,e.name,'read'));
    assert.equal(await page.locator('#entities button').count(),permitted.length);
    assert.equal(await page.locator('#business-admin').isVisible(),business.role_admin_roles.includes(actor.role));
    checks.add('business-browser-role-navigation');
    const metrics=business.metrics.filter(m=>allowed(actor.role,m.entity,'read_metrics'));
    assert.equal(await page.locator('#business-metrics section').count(),metrics.length);
    for(const metric of metrics) assert((await page.locator('#business-metrics').innerText()).includes(metric.label));
    if(metrics.length) { assert.equal(await page.locator('#business-metrics').evaluate(el=>getComputedStyle(el).display),'grid'); checks.add('business-browser-metrics'); }
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
    await page.waitForFunction(name=>document.querySelector('#rows').dataset.entity===name && document.querySelector('#rows').dataset.loading==='false',entity.name);
    const actions=page.locator('#rows tr').first().locator('td:last-child button');
    if(await actions.count()) {
      for(const width of [1440,390]) {
        await page.setViewportSize({width,height:1100});
        for(const end of [false,true]) {
          await page.locator('.table').evaluate((el,end)=>{el.scrollLeft=end?el.scrollWidth:0;},end);
          const bounds=await page.locator('.table').boundingBox();
          for(const button of await actions.all()) { const box=await button.boundingBox();assert(box && box.x>=bounds.x-1 && box.x+box.width<=bounds.x+bounds.width+1,'Action clipped at '+width+'px'); }
        }
      }
      await page.setViewportSize({width:1440,height:1100});
      await page.locator('.table').evaluate(el=>{el.scrollLeft=0;});
      checks.add('business-browser-responsive-actions');
    }
  }
  try {
    await verifySnapshot();
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
        if(allowed(actor.role,entity.name,'read_history')) {
          await page.locator('#business-notes').getByText(/Browser business acceptance note/).waitFor();
          const noteEventLabel=await page.evaluate(()=>EVENT_LABELS.note_added);
          assert.equal(typeof noteEventLabel,'string');assert(noteEventLabel.length>0);
          await page.locator('#business-history > p').filter({hasText:noteEventLabel}).waitFor();
        }
        checks.add('business-browser-notes-history');
      }
      if(workflow)await capture(actor,entity.name,'workflow');
      const visited=new Set();
      while(workflow&&!visited.has(row[workflow.status_field])) {
        visited.add(row[workflow.status_field]);
        const operation=workflow.transitions.find(t=>t.roles.includes(actor.role)&&t.from_states.includes(row[workflow.status_field]));
        if(!operation)break;
        const button=page.locator('#business-actions').getByRole('button',{name:operation.label||operation.name,exact:true});await button.waitFor();
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
    fs.writeFileSync(cfg.output,JSON.stringify({passed:true,real_browser:true,entities:cfg.spec.entities.map(e=>e.name),spec_digest:cfg.spec_digest,checks:[...checks],errors,evidence,screenshots:[...screenshots.values()]}));
  }finally{await browser.close();}
})().catch(error=>{console.error(browserFailure(error));process.exitCode=1;});
}
````
