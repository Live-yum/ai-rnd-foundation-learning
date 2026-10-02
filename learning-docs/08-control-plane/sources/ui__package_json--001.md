# ui/package.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 声明固定Vue/AntDesign及编译测试工具版本，提供dev/check/test/build命令；npm ci以相邻lock锁定完整依赖树。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/package.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L29。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`817`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/package.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7980df1ea80df17cdd1e4e41def51bcf4a13879471555e48e2599cb6a5c33ac3"} -->
````json
// ui/package.json
{
  "name": "ai-rnd-workbench-ui",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 127.0.0.1",
    "build": "vue-tsc --noEmit && vite build",
    "test": "vitest run",
    "check": "vue-tsc --noEmit",
    "format": "prettier --write \"src/**/*.{ts,vue,css}\" \"tests/**/*.ts\" *.json *.ts index.html",
    "format:check": "prettier --check \"src/**/*.{ts,vue,css}\" \"tests/**/*.ts\" *.json *.ts index.html"
  },
  "dependencies": {
    "@ant-design/icons-vue": "7.0.1",
    "ant-design-vue": "4.2.6",
    "vue": "3.5.30"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "5.2.4",
    "@vue/test-utils": "2.4.6",
    "jsdom": "26.1.0",
    "prettier": "3.6.2",
    "typescript": "5.9.3",
    "vite": "6.4.1",
    "vitest": "3.2.4",
    "vue-tsc": "3.2.5"
  }
}
````
