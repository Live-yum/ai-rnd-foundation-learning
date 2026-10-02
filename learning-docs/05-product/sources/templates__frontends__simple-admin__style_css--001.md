# templates/frontends/simple-admin/style.css · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：交付给产品的前端选项。** 轻量页面围绕产品规格显示字段和查询条件；注册登录后才请求业务API。清除筛选必须同时重置控件和查询状态，不能只隐藏标签；API-only模板则不需要管理页面。

**对应关系：** Selection → generator选取前端 → 产品HTTP/业务路由；verify-business-browser和test_business_python_browser。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/frontends/simple-admin/style.css`；**本文件共有 1 段**。本段覆盖源文件 L1–L109。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3284`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/frontends/simple-admin/style.css", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1e7b3e9fa5e022181fd80560aa527a1400e91955892e7f161d9f17769bb4d461"} -->
````css
/* templates/frontends/simple-admin/style.css */
:root {
  font-family: system-ui, sans-serif;
  color: #172033;
  background: #f4f6fa;
}
body {
  max-width: 1100px;
  margin: auto;
  padding: 24px;
}
header,
nav {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
header {
  justify-content: space-between;
}
main,
section,
dialog {
  background: white;
  padding: 20px;
  border-radius: 10px;
}
input,
select,
textarea,
button {
  font: inherit;
  padding: 9px;
  margin: 5px;
  border: 1px solid #b2bbcb;
  border-radius: 5px;
}
button {
  cursor: pointer;
  background: #e8eefc;
}
label {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}
#record-fields label {
  display: flex;
}
textarea {
  width: 85%;
  min-height: 100px;
}
table {
  border-collapse: collapse;
  width: 100%;
}
td,
th {
  padding: 10px;
  border-bottom: 1px solid #dfe4ed;
  text-align: left;
  max-width: 400px;
  overflow-wrap: anywhere;
}
.table {
  overflow-x: auto;
}
dialog {
  max-width: 750px;
  width: 85%;
  border: 1px solid #bac4d4;
}
#notice {
  min-height: 24px;
  color: #972621;
}
[hidden] {
  display: none !important;
}

/* Team business panels extend the existing lightweight admin visual system. */
#business-panels { padding: 16px 0; }
#business-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin: 12px 0 20px; }
#business-metrics .metric-card { margin: 0; padding: 16px; border: 1px solid #dfe4ed; background: #f8faff; min-width: 0; }
.metric-card h3 { margin: 0 0 12px; font-size: 15px; color: #47556b; }
.metric-value { margin: 0; font-size: 26px; font-weight: 650; }
.metric-chart { display: grid; gap: 10px; }
.metric-group { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 10px; font-size: 13px; }
.metric-label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.metric-track { grid-column: 1 / -1; height: 7px; background: #e4eaf5; border-radius: 5px; overflow: hidden; }
.metric-track span { display: block; height: 100%; background: #5676c5; border-radius: inherit; }
#business-notifications { max-height: 220px; overflow: auto; font-size: 14px; }
#business-notifications p { padding: 8px 0; margin: 0; border-bottom: 1px solid #edf0f5; }
#business-admin { margin: 12px 0; }
#business-users { max-height: 240px; overflow: auto; }
#record-fields label { display: grid; grid-template-columns: 110px minmax(0,1fr); margin: 8px 0; align-items: start; }
#record-fields input, #record-fields select, #record-fields textarea { box-sizing: border-box; margin: 0; width: 100%; }
dialog { max-height: 85vh; overflow: auto; }
dialog::backdrop { background: rgba(23,32,51,.28); }
@media (max-width: 600px) { body { padding: 12px; } main { padding: 12px; } #record-fields label { grid-template-columns: 1fr; } #business-metrics { grid-template-columns: 1fr; } }

.table table { min-width: 960px; }
.table th { white-space: nowrap; }
.table td { min-width: 90px; max-width: 240px; overflow-wrap: normal; word-break: normal; }
.table td:last-child { min-width: 200px; }
.table th:last-child, .table td:last-child { width: 235px; position: sticky; right: 0; background: white; box-shadow: -4px 0 6px rgba(23,32,51,.05); z-index: 1; }
.table td:last-child { min-width: 235px; white-space: nowrap; }
````
