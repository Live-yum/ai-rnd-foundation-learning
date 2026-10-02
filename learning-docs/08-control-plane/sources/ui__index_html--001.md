# ui/index.html · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** Vite开发与构建的HTML入口；源入口由编译器替换为生产静态资源引用。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/index.html`；**本文件共有 1 段**。本段覆盖源文件 L1–L14。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`425`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/index.html", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0541210f85022a8318491e70177feb7011d98bd05643e8209f208892a8d1bf00"} -->
````html
<!-- ui/index.html -->
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="color-scheme" content="light" />
    <meta name="referrer" content="no-referrer" />
    <title>AI 研发平台 · 本地工作空间</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
````
