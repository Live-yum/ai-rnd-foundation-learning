# tools/daytona/api-digest-reference.patch · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/api-digest-reference.patch`；**本文件共有 1 段**。本段覆盖源文件 L1–L12。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`373`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/api-digest-reference.patch", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d547f0e6dc75aea73b1fd907fd7cebe928d11782f18230ffec212c4cbc31a437"} -->
````text
# tools/daytona/api-digest-reference.patch
--- a/apps/api/src/common/utils/docker-image.util.ts
+++ b/apps/api/src/common/utils/docker-image.util.ts
@@ -43,7 +43,8 @@
       name = `${this.registry}/${name}`
     }
     if (this.tag) {
-      name = `${name}:${this.tag}`
+      const separator = this.tag.startsWith('sha256:') ? '@' : ':'
+      name = `${name}${separator}${this.tag}`
     }
     return name
   }
````
