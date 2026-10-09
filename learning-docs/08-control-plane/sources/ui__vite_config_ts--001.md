# ui/vite.config.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 配置Vue编译和开发期API代理，生产资源写到workbench/web供本机FastAPI与wheel使用；开发代理不是生产部署。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/vite.config.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L35。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`827`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/vite.config.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bb9220b034f09eded3b82ee38f511b5897a0ac484bb7d56226cecfdf49dd5e51"} -->
````typescript
// ui/vite.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
export default defineConfig({
  plugins: [vue()],
  base: '/ui/',
  build: {
    outDir: '../workbench/web',
    emptyOutDir: true,
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        entryFileNames: 'app.js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name][extname]',
        inlineDynamicImports: true,
      },
    },
  },
  server: {
    proxy: Object.fromEntries(
      [
        '/projects',
        '/batches',
        '/runs',
        '/models',
        '/settings',
        '/catalog',
        '/templates',
        '/health',
        '/ready',
      ].map((p) => [p, 'http://127.0.0.1:8000']),
    ),
  },
  test: { environment: 'jsdom', include: ['tests/**/*.test.ts'], restoreMocks: true },
})
````
