# workbench/web/style.css · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：工作台浏览器界面。** HTML提供控件与容器，CSS控制布局，JavaScript绑定事件并调用/api接口。界面先保存技术栈选择，再创建运行、读取状态、回答关卡或委托智能推荐；认证令牌只发给同一本机工作台。

**对应关系：** 网页事件 → api路由 → Store/Runtime → 状态JSON → 页面重新渲染；ci_guided_browser。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `workbench/web/style.css`；**本文件共有 1 段**。本段覆盖源文件 L1–L72。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1029`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/web/style.css", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8763de75d3ae515dc74342e3c4411c1682f450c9bd08754612f8a7fb444c24c4"} -->
````css
/* workbench/web/style.css */
:root {
  font-family: system-ui, sans-serif;
  color: #15243c;
  background: #f3f5f9;
}
body {
  margin: auto;
  padding: 24px;
  max-width: 1080px;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}
section {
  background: white;
  border: 1px solid #dce2ec;
  padding: 22px;
  margin: 15px 0;
  border-radius: 10px;
}
input,
select,
textarea,
button {
  font: inherit;
  padding: 10px;
  margin: 5px;
  border: 1px solid #acb7ca;
  border-radius: 5px;
}
label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
#new-run label {
  display: flex;
}
textarea {
  width: 95%;
}
button {
  background: #e8f0ff;
  cursor: pointer;
}
button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}
#smart {
  background: #153f88;
  color: white;
}
#notice {
  color: #9b203a;
  min-height: 25px;
}
pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
code {
  background: #edf1f7;
  padding: 2px 5px;
}
[hidden] {
  display: none !important;
}
````
