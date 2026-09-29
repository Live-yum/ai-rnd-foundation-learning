"use strict";
const $ = (id) => document.getElementById(id);
let token = sessionStorage.getItem("product-token") || "",
  spec,
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
    field.name,
    mode === "record" ? $("record-fields") : $("filter-fields"),
  );
  let input;
  if (field.kind === "enum" || field.kind === "boolean") {
    input = node("select", undefined, label);
    if (!field.required || mode !== "record")
      node("option", "", input).value = "";
    const values = field.kind === "boolean" ? ["true", "false"] : field.choices;
    for (const value of values) node("option", value, input).value = value;
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
  entity = current;
  offset = 0;
  $("entity-title").textContent = entity.description || entity.name;
  $("filter-fields").replaceChildren();
  if (entity.fields.some((f) => f.searchable)) {
    const label = node("label", "关键词", $("filter-fields"));
    const q = node("input", undefined, label);
    q.name = "q";
    q.placeholder = "搜索标题 / 正文";
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
  const query = new URLSearchParams();
  for (const [key, value] of new FormData($("filters")))
    if (value) query.set(key, value);
  query.set("offset", String(offset));
  query.set("limit", "50");
  const response = await api("/api/" + entity.name + "?" + query);
  const rows = await response.json();
  if (sequence !== loadSequence) return;
  total = Number(response.headers.get("X-Total-Count"));
  if (sequence !== loadSequence) return;
  $("total").textContent = `共 ${total} 条，当前从 ${offset + 1} 开始`;
  $("columns").replaceChildren();
  const head = node("tr", undefined, $("columns"));
  entity.fields.forEach((f) => node("th", f.name, head));
  node("th", "操作", head);
  $("rows").replaceChildren();
  for (const row of rows) {
    const tr = node("tr", undefined, $("rows"));
    for (const field of entity.fields) node("td", row[field.name] ?? "", tr);
    const cell = node("td", undefined, tr);
    node("button", "编辑", cell).onclick = () => edit(row);
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
}
function edit(row) {
  editing = row?.id || null;
  $("edit-title").textContent = editing ? "编辑" : "新增";
  $("record-fields").replaceChildren();
  for (const field of entity.fields) {
    const input = control(field);
    if (row && row[field.name] !== null) input.value = String(row[field.name]);
  }
  $("editor").showModal();
}
async function signedIn() {
  const data = await (await api("/schema")).json();
  spec = data.spec;
  $("title").textContent = spec.title;
  $("login").hidden = true;
  $("workspace").hidden = false;
  $("logout").hidden = false;
  $("entities").replaceChildren();
  for (const e of spec.entities)
    node("button", e.description || e.name, $("entities")).onclick = () =>
      choose(e);
  choose(spec.entities[0]);
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
$("create").onclick = () => edit(null);
$("cancel").onclick = () => $("editor").close();
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
      let v = raw[field.name];
      data[field.name] =
        v === "" && !field.required
          ? null
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
