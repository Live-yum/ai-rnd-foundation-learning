# ui/tsconfig.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 让Vue与TypeScript检查脚本、组件和测试的类型，不把类型检查通过当作浏览器交互通过。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tsconfig.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L17。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`473`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tsconfig.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "73d81ec4a09e63820864db21c964a738158c63f4fc0cf6a1ef9525c9076e27a7"} -->
````json
// ui/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "types": ["vite/client"],
    "moduleResolution": "Bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "strict": true
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "vite.config.ts", "tests/**/*.ts"]
}
````
