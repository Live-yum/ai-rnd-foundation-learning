"use strict";
const $ = (id) => document.getElementById(id);
let token = sessionStorage.getItem("workbench-token") || "",
  catalog = [],
  runId = "",
  state = null,
  timer = null,
  selected = null;
const txt = (id, value) => {
  $(id).textContent = value ?? "";
};
function inform(error) {
  txt("notice", error.message || String(error));
}
async function api(path, method = "GET", body) {
  const headers = { Authorization: "Bearer " + token };
  if (method !== "GET") {
    headers["Content-Type"] = "application/json";
    headers["Idempotency-Key"] = crypto.randomUUID();
  }
  const r = await fetch(path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!r.ok) {
    const b = await r.json();
    throw new Error(
      typeof b.detail === "string" ? b.detail : JSON.stringify(b.detail),
    );
  }
  return r.json();
}
function options(id, values) {
  $(id).replaceChildren();
  for (const [value, label] of values) {
    const o = document.createElement("option");
    o.value = value;
    o.textContent = label;
    $(id).append(o);
  }
}
function templateChanged() {
  const chosen = catalog.find((x) => x.template === $("template").value);
  options(
    "frontend",
    chosen.frontends.map((v) => [v, v]),
  );
  options(
    "database",
    chosen.databases.map((v) => [v, v]),
  );
  txt(
    "capabilities",
    `数据归属：${(chosen.scopes || [chosen.scope]).join(" / ")}；基础能力：${chosen.features.join(" / ")}。声明式业务合同：角色与行范围、关联、分配、状态、处理记录、站内提醒和统计；仅限已登记动作，不执行任意跨实体脚本。${chosen.template === "python-basic" ? "SQLite免服务，PostgreSQL另需数据库/Docker。" : "原生模式需要Linux/WSL、Java或Python、Node、PostgreSQL、Redis；代码快照已包含在仓库。"}`,
  );
  $("request").hidden = true;
  selected = null;
}
async function connect() {
  token = $("token").value.trim() || token;
  catalog = await api("/catalog");
  sessionStorage.setItem("workbench-token", token);
  $("authorization").hidden = true;
  $("app").hidden = false;
  options(
    "template",
    catalog.map((x) => [x.template, x.name]),
  );
  templateChanged();
  txt("models", JSON.stringify(await api("/models"), null, 2));
  await listRuns();
}
async function listRuns() {
  const list = await api("/runs");
  options(
    "runs",
    list.map((x) => [x.id, `${x.template} · ${x.status} · ${x.id}`]),
  );
}
async function update() {
  if (!runId) return;
  state = await api("/runs/" + runId);
  $("current").hidden = false;
  txt("run-title", "运行 " + runId);
  txt("status", "状态：" + state.status);
  txt(
    "auto-state",
    state.auto_mode
      ? "智能推荐已启用：后续不再询问，由AI决定未明确项，测试仍是门禁。"
      : "人工确认模式",
  );
  const finished = ["READY", "SOURCE_READY", "REJECTED"].includes(state.status);
  $("smart").disabled = finished || state.auto_mode;
  $("manual").disabled = finished || !state.auto_mode;
  $("download").hidden = !["READY", "SOURCE_READY"].includes(state.status);
  $("retry").hidden = !["FAILED", "BLOCKED", "PAUSED_LIMIT"].includes(
    state.status,
  );
  const pending = state.pending;
  const data = pending?.data;
  txt(
    "summary",
    state.error || data?.requirement?.summary || data?.plan?.title || "",
  );
  $("questions").replaceChildren();
  for (const q of data?.requirement?.questions || []) {
    const p = document.createElement("p");
    p.textContent = q;
    $("questions").append(p);
  }
  for (const q of data?.requirement?.recommendations || []) {
    const p = document.createElement("p");
    p.textContent = "推荐：" + q;
    $("questions").append(p);
  }
  $("answer-form").hidden = !pending;
  $("approve").disabled = !pending?.can_approve;
  $("answer-button").disabled = !(
    pending?.actions.includes("answer") || pending?.actions.includes("revise")
  );
  txt("details", JSON.stringify(state, null, 2));
  txt(
    "events",
    JSON.stringify(await api("/runs/" + runId + "/events"), null, 2),
  );
  txt(
    "used-models",
    JSON.stringify(await api("/runs/" + runId + "/models"), null, 2),
  );
  if (timer) clearTimeout(timer);
  if (!finished) timer = setTimeout(() => update().catch(inform), 1200);
}
$("connect").onsubmit = (e) => {
  e.preventDefault();
  connect().catch(inform);
};
$("template").onchange = templateChanged;
$("frontend").onchange = () => {
  $("request").hidden = true;
  selected = null;
};
$("database").onchange = $("frontend").onchange;
$("choose").onclick = () => {
  selected = {
    template: $("template").value,
    frontend: $("frontend").value,
    database: $("database").value,
  };
  $("request").hidden = false;
};
$("new-run").onsubmit = async (e) => {
  e.preventDefault();
  try {
    if (!selected) throw new Error("先选择前后端与数据库");
    const p = await api("/projects", "POST", {
      title: $("project-title").value,
    });
    const r = await api(`/projects/${p.id}/runs`, "POST", {
      template: selected.template,
      selection: selected,
      requirement: $("requirement").value,
      intelligent: $("initial-smart").checked,
    });
    runId = r.run_id;
    await listRuns();
    await update();
  } catch (error) {
    inform(error);
  }
};
$("open-run").onclick = () => {
  runId = $("runs").value;
  update().catch(inform);
};
$("refresh-runs").onclick = () => listRuns().catch(inform);
async function decide(action) {
  if (!state?.pending) throw new Error("当前没有等待项");
  const body = { gate_id: state.pending.gate_id, action };
  if (action === "answer" || action === "revise") body.text = $("answer").value;
  else body.approved = action === "approve";
  await api("/runs/" + runId + "/resume", "POST", body);
  $("answer").value = "";
  await update();
}
$("answer-form").onsubmit = (e) => {
  e.preventDefault();
  decide(state.pending.actions.includes("answer") ? "answer" : "revise").catch(
    inform,
  );
};
$("approve").onclick = () => decide("approve").catch(inform);
$("reject").onclick = () => decide("reject").catch(inform);
$("smart").onclick = () =>
  api("/runs/" + runId + "/automation", "POST", {
    enabled: true,
    accepted: true,
  })
    .then(update)
    .catch(inform);
$("manual").onclick = () =>
  api("/runs/" + runId + "/automation", "POST", {
    enabled: false,
    accepted: false,
  })
    .then(update)
    .catch(inform);
$("retry").onclick = () =>
  api("/runs/" + runId + "/retry", "POST")
    .then(update)
    .catch(inform);
$("download").onclick = async () => {
  try {
    const r = await fetch(`/runs/${runId}/download`, {
      headers: { Authorization: "Bearer " + token },
    });
    if (!r.ok) throw new Error("交付下载失败");
    const url = URL.createObjectURL(await r.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = runId + ".zip";
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) {
    inform(error);
  }
};
if (token) connect().catch(inform);
