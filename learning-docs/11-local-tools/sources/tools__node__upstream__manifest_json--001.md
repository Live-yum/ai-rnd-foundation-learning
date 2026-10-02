# tools/node/upstream/manifest.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：固定的Continue开源全文索引组件及许可证。** TypeScript源码原样保留，manifest记录上游提交、Git对象哈希与SHA256，构建前逐个验证。这里只嵌入全文索引组件，不加载Continue的IDE、账户或托管服务；LICENSE必须随源码保留。

**对应关系：** npm run build --prefix tools/node → esbuild绑定本机host → continue_index调用；独立SQLite缓存。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/node/upstream/manifest.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L16。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`595`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/node/upstream/manifest.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "448350d48dfdcebe11d52b3ad59c44cae01f22bf4e0b2170eb8cc779bbc2369a"} -->
````json
// tools/node/upstream/manifest.json
{
  "repository": "https://github.com/continuedev/continue",
  "revision": "5522c6f44ca0ac3528b37244818fbfa39b5af470",
  "files": {
    "FullTextSearchCodebaseIndex.ts": {
      "path": "core/indexing/FullTextSearchCodebaseIndex.ts",
      "git_blob_sha1": "8016d04d3eddc84ec48ffa517ba96b2caba9b14e",
      "sha256": "ef2e80c7db63f3148fe8894f2ea4fbd23e57148f2f33b7cec55620c51ec16c60"
    },
    "LICENSE": {
      "path": "LICENSE",
      "git_blob_sha1": "c25dc1768217ba50d454fcc06290d66886512872",
      "sha256": "b14a17598cb08c4c7c82c070731126304e0a75d001ed59fb9ea3955a0b561802"
    }
  }
}
````
