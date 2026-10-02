# templates/frontends/simple-admin/app.js · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：交付给产品的前端选项。** 轻量页面围绕产品规格显示字段和查询条件；注册登录后才请求业务API。清除筛选必须同时重置控件和查询状态，不能只隐藏标签；API-only模板则不需要管理页面。

**对应关系：** Selection → generator选取前端 → 产品HTTP/业务路由；verify-business-browser和test_business_python_browser。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/frontends/simple-admin/app.js`；**本文件共有 1 段**。本段覆盖源文件 L1–L414。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`21158`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/frontends/simple-admin/app.js", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1919345d3c001796a2f34e0e6e24bde24d760cf1c0102532fd1a6eca7bf582c6"} -->
````javascript
// templates/frontends/simple-admin/app.js
"use strict";
const $ = (id) => document.getElementById(id);
let token = sessionStorage.getItem("product-token") || "",
  spec,
  businessActor,
  businessPermissions = {},
  detailRecord = null,
  detailSequence = 0,
  editorSequence = 0,
  entity,
  offset = 0,
  total = 0,
  editing = null,
  loadSequence = 0;
function node(tag, text, parent) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = String(text);
  if (parent) parent.append(element);
  return element;
}
const EVENT_LABELS = {created:"已创建", updated:"已更新", assigned:"已分配", transitioned:"状态已更新", note_added:"新增处理记录", archived:"已归档", due:"即将到期", overdue:"已逾期", resolved:"已解决"};
function fieldLabel(name) { return entity?.fields.find(field=>field.name===name)?.label || name; }
function entityLabel(name) { return spec?.entities.find(item => item.name === name)?.description || name; }
function displayTime(value) { const date = new Date(value); return Number.isNaN(date.getTime()) ? value : date.toLocaleString("zh-CN", {hour12:false,timeZone:"UTC"}) + " UTC"; }
function actionLabel(action, chosen) {
  if (action.startsWith("transitioned:")) {
    const name = action.slice("transitioned:".length);
    const transition = spec.business.workflows.find(item => item.entity === chosen.name)?.transitions.find(item => item.name === name);
    return transition?.label || name;
  }
  return EVENT_LABELS[action] || action;
}
function actorLabel(item) { return item.actor_username || "未知用户"; }
function inform(error) {
  $("notice").textContent = error.message || String(error);
}
async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + token,
      ...options.headers,
    },
  });
  if (!response.ok) {
    let body = await response.json();
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail),
    );
  }
  return response;
}
function control(field, mode = "record", name = field.name) {
  const label = node(
    "label",
    field.kind === "datetime" ? fieldLabel(field.name) + "（UTC）" : fieldLabel(field.name),
    mode === "record" ? $("record-fields") : $("filter-fields"),
  );
  let input;
  if (field.kind === "enum" || field.kind === "boolean") {
    input = node("select", undefined, label);
    if (!field.required || mode !== "record")
      node("option", "", input).value = "";
    const values = field.kind === "boolean" ? ["true", "false"] : field.choices;
    for (const value of values) node("option", field.choice_labels?.[value] || value, input).value = value;
  } else {
    input = node(
      field.kind === "text" && field.max_length > 500 && mode === "record"
        ? "textarea"
        : "input",
      undefined,
      label,
    );
    if (field.kind === "integer") {
      input.type = "number";
      input.step = "1";
    } else if (field.kind === "date") input.type = "date";
    else if (field.kind === "datetime") input.type = "datetime-local";
    else {
      input.maxLength = field.max_length;
      input.minLength = field.min_length || 0;
    }
  }
  input.name = name;
  input.dataset.kind = field.kind;
  input.required = mode === "record" && field.required;
  return input;
}
function choose(current) {
  ++detailSequence; ++editorSequence;
  if ($("business-detail").open) $("business-detail").close();
  if ($("editor").open) $("editor").close();
  entity = current;
  if (spec?.business) $("create").hidden = !can("create");
  offset = 0;
  $("entity-title").textContent = entity.description || entity.name;
  $("filter-fields").replaceChildren();
  if (entity.fields.some((f) => f.searchable)) {
    const label = node("label", "关键词", $("filter-fields"));
    const q = node("input", undefined, label);
    q.name = "q";
    q.placeholder = "搜索可检索字段";
  }
  for (const field of entity.fields) {
    if (field.filterable) control(field, "filter", "filter_" + field.name);
    if (field.date_range) {
      for (const prefix of ["from_", "to_"]) {
        const label = node(
          "label",
          prefix === "from_" ? "起始日期" : "结束日期",
          $("filter-fields"),
        );
        const input = node("input", undefined, label);
        input.type = "date";
        input.name = prefix + field.name;
      }
    }
  }
  load().catch(inform);
}
async function load() {
  const sequence = ++loadSequence;
  $("rows").dataset.loading="true";
  const query = new URLSearchParams();
  for (const [key, value] of new FormData($("filters")))
    if (value) query.set(key, value);
  query.set("offset", String(offset));
  query.set("limit", "50");
  const response = await api("/api/" + entity.name + "?" + query);
  const rows = await response.json();
  if (sequence !== loadSequence) return;
  const chosen=entity;
  let labels={};
  if(spec.business && rows.length) labels=await(await api(`/business/labels/${chosen.name}`, {method:"POST",body:JSON.stringify({record_ids:rows.map(row=>row.id)})})).json();
  if(sequence!==loadSequence || entity!==chosen)return;
  total = Number(response.headers.get("X-Total-Count"));
  if (sequence !== loadSequence) return;
  $("total").textContent = `共 ${total} 条，当前从 ${offset + 1} 开始`;
  $("columns").replaceChildren();
  const head = node("tr", undefined, $("columns"));
  entity.fields.forEach((f) => node("th", fieldLabel(f.name), head));
  node("th", "操作", head);
  $("rows").replaceChildren();
  for (const row of rows) {
    const tr = node("tr", undefined, $("rows"));
    tr.dataset.id = row.id;
    for (const field of entity.fields) {
      const raw=row[field.name]; let value=raw??(spec.business?"—":"");
      const relation=spec.business?.relations.find(item=>item.entity===entity.name&&item.field===field.name);
      if(raw && relation) value=labels[field.name]?.[String(raw)] || "关联记录不可见";
      else if(raw && field.kind==="datetime") value=displayTime(raw);
      else if(field.kind==="enum") value=field.choice_labels?.[String(raw)]||raw;
      const cell=node("td",value,tr); cell.title=String(value); if(relation)cell.dataset.reference=String(raw||"");
    }
    const cell = node("td", undefined, tr);
    if (!spec.business || can("update")) node("button", "编辑", cell).onclick = () => edit(row);
    if (spec.business) {
      node("button", "详情 / 处理", cell).onclick = () => showBusinessDetail(row).catch(inform);
      if (can("archive")) node("button", "归档", cell).onclick = async () => {
        if (!confirm("归档保留记录及历史，是否继续？")) return;
        try { await api(`/api/${entity.name}/${row.id}/archive`, {method:"POST"}); await load(); }
        catch(error) { inform(error); }
      };
      continue;
    }
    node("button", "删除", cell).onclick = async () => {
      if (!confirm("删除这条记录？")) return;
      try {
        await api(`/api/${entity.name}/${row.id}`, { method: "DELETE" });
        await load();
      } catch (error) {
        inform(error);
      }
    };
  }
  $("rows").dataset.entity=chosen.name;
  $("rows").dataset.loading="false";
}
async function edit(row) {
  const sequence = ++editorSequence, chosen = entity;
  editing = row?.id || null;
  $("edit-title").textContent = editing ? "编辑" : "新增";
  $("record-fields").replaceChildren();
  for (const field of chosen.fields) {
    if (sequence !== editorSequence || chosen !== entity) return;
    if (spec.business && protectedFields().has(field.name)) continue;
    let input;
    const relation = spec.business?.relations.find(r => r.entity === entity.name && r.field === field.name);
    if (relation && relation.target_entity !== "$users") {
      const label = node("label", fieldLabel(field.name), $("record-fields"));
      input = node("select", undefined, label); input.name = field.name; input.required = field.required;
      node("option", "", input).value = "";
      const related = await (await api(`/api/${relation.target_entity}?limit=100`)).json();
      if (sequence !== editorSequence || chosen !== entity) return;
      for (const item of related) node("option", item.name || item.title || item.id, input).value = item.id;
    } else input = control(field);
    if (row && row[field.name] !== null) input.value = field.kind === "datetime" ? String(row[field.name]).replace(/Z$/, "").slice(0,16) : String(row[field.name]);
  }
  if (sequence === editorSequence && chosen === entity) $("editor").showModal();
}
async function signedIn() {
  const data = await (await api("/schema")).json();
  spec = data.spec;
  businessActor = data.actor; businessPermissions = data.permissions || {};
  $("business-panels").hidden = !spec.business;
  if (spec.business) {
    $("business-role").textContent = `${businessActor.username} · ${spec.business.roles.find(role => role.name === businessActor.role)?.label || businessActor.role}`;
    $("register").hidden = !spec.business.registration.enabled;
    await refreshBusiness();
  }
  $("title").textContent = spec.title;
  $("login").hidden = true;
  $("workspace").hidden = false;
  $("logout").hidden = false;
  $("entities").replaceChildren();
  const available = spec.business ? spec.entities.filter(e => businessPermissions[e.name]?.actions.includes("read")) : spec.entities;
  for (const e of available)
    node("button", e.description || e.name, $("entities")).onclick = () =>
      choose(e);
  if (available.length) choose(available[0]);
  else { $("create").hidden=true; $("entity-title").textContent="当前角色暂无可访问的数据"; }
}
async function authenticate(register) {
  try {
    const data = Object.fromEntries(new FormData($("auth")));
    const response = await api("/auth/" + (register ? "register" : "login"), {
      method: "POST",
      body: JSON.stringify(data),
    });
    token = (await response.json()).access_token;
    sessionStorage.setItem("product-token", token);
    $("notice").textContent = "";
    await signedIn();
  } catch (error) {
    inform(error);
  }
}
$("auth").onsubmit = (e) => {
  e.preventDefault();
  authenticate(false);
};
$("register").onclick = () => authenticate(true);
$("logout").onclick = () => {
  sessionStorage.removeItem("product-token");
  location.reload();
};
$("filters").onsubmit = (e) => {
  e.preventDefault();
  offset = 0;
  load().catch(inform);
};
$("reset").onclick = () => {
  // A child whose id is reset shadows the form.reset property in browsers.
  HTMLFormElement.prototype.reset.call($("filters"));
  offset = 0;
  load().catch(inform);
};
$("create").onclick = () => edit(null).catch(inform);
$("cancel").onclick = () => { ++editorSequence; $("editor").close(); };
$("previous").onclick = () => {
  offset = Math.max(0, offset - 50);
  load().catch(inform);
};
$("next").onclick = () => {
  if (offset + 50 < total) {
    offset += 50;
    load().catch(inform);
  }
};
$("record").onsubmit = async (e) => {
  e.preventDefault();
  try {
    const raw = Object.fromEntries(new FormData($("record")));
    const data = {};
    for (const field of entity.fields) {
      if (spec.business && protectedFields().has(field.name)) continue;
      let v = raw[field.name];
      data[field.name] =
        v === "" && !field.required
          ? null
          : field.kind === "datetime"
            ? new Date(v + "Z").toISOString()
          : field.kind === "integer"
            ? Number(v)
            : field.kind === "boolean"
              ? v === "true"
              : v;
    }
    await api("/api/" + entity.name + (editing ? "/" + editing : ""), {
      method: editing ? "PUT" : "POST",
      body: JSON.stringify(data),
    });
    $("editor").close();
    await load();
    $("notice").textContent = "已保存";
  } catch (error) {
    inform(error);
  }
};
if (token)
  signedIn().catch(() => {
    token = "";
    sessionStorage.removeItem("product-token");
  });


function can(action) { return businessPermissions[entity?.name]?.actions.includes(action); }
function protectedFields() {
  const result = new Set(["id","owner_id","created_by","created_at","updated_at","archived_at"]);
  const resource = spec.business.resources.find(r => r.entity === entity.name);
  if (resource?.assignee_field) result.add(resource.assignee_field);
  const workflow = spec.business.workflows.find(w => w.entity === entity.name);
  if (workflow) { result.add(workflow.status_field); workflow.transitions.forEach(t => { if(t.set_timestamp) result.add(t.set_timestamp); }); }
  return result;
}
async function refreshBusiness() {
  const metrics = await (await api("/business/metrics")).json();
  $("business-metrics").replaceChildren();
  for (const metric of metrics) {
    const card = node("section", undefined, $("business-metrics")); card.className="metric-card";
    node("h3", metric.label, card);
    if (metric.groups) {
      const definition=spec.business.metrics.find(item => item.name===metric.name);
      const relation=spec.business.relations.find(item => item.entity===definition?.entity && item.field===definition?.group_by && item.target_entity!=="$users");
      let labels={};
      if(relation) { try { const related=await(await api(`/api/${relation.target_entity}?limit=100`)).json(); labels=Object.fromEntries(related.map(row=>[String(row.id),row.name||row.title||row.id])); } catch (_) { /* Authorized aggregates may omit direct record access. */ } }
      const maximum=Math.max(1,...metric.groups.map(group=>Number(group.count)||0));
      const chart=node("div",undefined,card); chart.className="metric-chart"; chart.setAttribute("role","list"); chart.setAttribute("aria-label",metric.label);
      for(const group of metric.groups) {
        const raw=group.day??group.key??"未分类"; const label=labels[String(raw)]||raw;
        const row=node("div",undefined,chart); row.className="metric-group"; row.setAttribute("role","listitem");
        const caption=node("span",label,row);caption.className="metric-label";caption.title=String(label);
        node("strong",group.count,row);
        const track=node("div",undefined,row);track.className="metric-track";const bar=node("span",undefined,track);bar.style.width=`${Math.max(0,Number(group.count)||0)/maximum*100}%`;
      }
      if(!metric.groups.length) node("p","暂无数据",chart);
    } else {
      const definition=spec.business.metrics.find(item=>item.name===metric.name);
      const value=typeof metric.value==="number" ? new Intl.NumberFormat("zh-CN",{maximumFractionDigits:2}).format(metric.value) : metric.value;
      const unit=definition?.kind==="average_duration" && metric.unit==="seconds" ? " 秒" : "";
      node("p",metric.value===null?"暂无已完成记录":`${value}${unit}`,card).className="metric-value";
    }
  }
  const notifications = await (await api("/business/notifications")).json(); $("business-notifications").replaceChildren();
  if(!notifications.length) node("p","暂无站内提醒",$("business-notifications"));
  for (const item of notifications) { const line = node("p", `${EVENT_LABELS[item.event] || item.event} · ${entityLabel(item.entity)} · ${displayTime(item.created_at)}`, $("business-notifications"));
    if (!item.read_at) node("button", "标记已读", line).onclick = async () => { try { await api(`/business/notifications/${item.id}/read`, {method:"POST"}); await refreshBusiness(); } catch(error) {inform(error);} };
  }
  const admin = spec.business.role_admin_roles.includes(businessActor.role); $("business-admin").hidden = !admin;
  if (admin) {
    $("business-new-role").replaceChildren(); spec.business.roles.forEach(role => node("option", role.label, $("business-new-role")).value = role.name);
    const users = await (await api("/business/users")).json(); $("business-users").replaceChildren();
    for (const user of users) { const line = node("p", user.username, $("business-users")); const roles=node("select", undefined,line);
      spec.business.roles.forEach(role => node("option", role.label, roles).value=role.name); roles.value=user.role;
      node("button", "更新角色",line).onclick=async()=>{try{await api(`/business/users/${user.id}/role`,{method:"PUT",body:JSON.stringify({role:roles.value})});await refreshBusiness();}catch(error){inform(error);}};
    }
  }
}
async function showBusinessDetail(row) {
  const sequence=++detailSequence, chosen=entity;
  detailRecord = row; $("business-detail-title").textContent = row.name || row.title || row.id;
  $("business-actions").replaceChildren(); $("business-notes").replaceChildren(); $("business-history").replaceChildren(); $("business-related").replaceChildren();
  if(can("assign")) {
    const assignees=await(await api(`/business/users?entity=${chosen.name}`)).json();
    if(sequence!==detailSequence || chosen!==entity) return;
    const select=node("select",undefined,$("business-actions")); select.id="business-assignee";
    node("option","未分配",select).value=""; assignees.forEach(user=>node("option",user.username,select).value=user.id);
    const field=spec.business.resources.find(r=>r.entity===entity.name).assignee_field; select.value=row[field]||"";
    node("button","分配",$("business-actions")).onclick=async()=>{try{const updated=await(await api(`/api/${entity.name}/${row.id}/assign`,{method:"POST",body:JSON.stringify({user_id:select.value||null})})).json();await showBusinessDetail(updated);await load();}catch(error){inform(error);}};
  }
  const workflow=spec.business.workflows.find(w=>w.entity===entity.name);
  if(workflow && can("transition")) for(const action of workflow.transitions.filter(t=>t.roles.includes(businessActor.role)&&t.from_states.includes(row[workflow.status_field]))) {
    node("button",action.label||action.name,$("business-actions")).onclick=async()=>{try{const updated=await(await api(`/api/${entity.name}/${row.id}/transition`,{method:"POST",body:JSON.stringify({transition:action.name})})).json();await showBusinessDetail(updated);await load();await refreshBusiness();}catch(error){inform(error);}};
  }
  if(can("read_history")) {
    const notes=await(await api(`/api/${chosen.name}/${row.id}/notes`)).json();
    if(sequence!==detailSequence || chosen!==entity) return;
    notes.forEach(note=>node("p",`${displayTime(note.created_at)} · ${actorLabel(note)}：${note.body}`,$("business-notes")));
  }
  if(can("read_history") || can("read_audit")) {
    const history=await(await api(`/api/${chosen.name}/${row.id}/history`)).json();
    if(sequence!==detailSequence || chosen!==entity) return;
    history.forEach(item=>{
      node("p",`${displayTime(item.created_at)} · ${actorLabel(item)} · ${actionLabel(item.action, chosen)}`,$("business-history"));
      if(Object.hasOwn(item,"before") || Object.hasOwn(item,"after")) {
        const details=node("details",undefined,$("business-history"));
        node("summary","查看审计详情（原始 JSON）",details);
        node("pre",JSON.stringify(item,null,2),details);
      }
    });
  }
  const related=await(await api(`/business/related/${chosen.name}/${row.id}`)).json();
  if(sequence!==detailSequence || chosen!==entity) return;
  for(const group of related) {node("h4",entityLabel(group.entity),$("business-related"));group.records.forEach(item=>{
      const workflow=spec.business.workflows.find(w=>w.entity===group.entity);
      const field=spec.entities.find(target=>target.name===group.entity)?.fields.find(field=>field.name===workflow?.status_field);
      const status=workflow ? item[workflow.status_field] : null;
      const text=(item.name||item.title||item.id)+(workflow ? " · "+(field?.choice_labels?.[status]||status) : "");
      node("button",text,$("business-related")).onclick=async()=>{try{const target=spec.entities.find(e=>e.name===group.entity);if(target){choose(target);await showBusinessDetail(item);}}catch(error){inform(error);}};
    });if(!group.records.length)node("p","暂无关联记录",$("business-related"));}
  $("business-note-form").hidden=!can("add_note");
  if(sequence!==detailSequence || chosen!==entity) return;
  if(!$("business-detail").open) $("business-detail").showModal();
}
$("refresh-business").onclick=()=>refreshBusiness().catch(inform);
$("business-close").onclick=()=>{++detailSequence;$("business-detail").close();};
$("business-detail").addEventListener("cancel",()=>{++detailSequence;});
$("business-note-form").onsubmit=async(event)=>{event.preventDefault();try{await api(`/api/${entity.name}/${detailRecord.id}/notes`,{method:"POST",body:JSON.stringify(Object.fromEntries(new FormData(event.target)))});event.target.reset();await showBusinessDetail(detailRecord);}catch(error){inform(error);}};
$("business-create-user").onsubmit=async(event)=>{event.preventDefault();try{await api("/business/users",{method:"POST",body:JSON.stringify(Object.fromEntries(new FormData(event.target)))});event.target.reset();await refreshBusiness();}catch(error){inform(error);}};

setInterval(() => { if (spec?.business && token && !document.hidden) refreshBusiness().catch(inform); }, 60000);
````
