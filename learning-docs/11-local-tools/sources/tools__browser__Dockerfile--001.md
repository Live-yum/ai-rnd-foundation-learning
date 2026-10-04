# tools/browser/Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/browser/Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L11。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`736`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/browser/Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f072619286d03c53af3605385fcaf1e5b3fbd4427fac8467dbcf761953fcb03f"} -->
````dockerfile
# tools/browser/Dockerfile
# Build-time network is only for pinned official tooling; runtime has no network.
FROM mcr.microsoft.com/playwright:v1.56.1-noble
WORKDIR /opt/verifier
RUN npm install --ignore-scripts --no-audit --no-fund --package-lock=false playwright@1.56.1
COPY scripts/capability_browser.cjs scripts/capability_browser_worker.cjs scripts/capability_browser_network_probe.cjs ./
COPY tools/browser/Dockerfile ./Dockerfile
COPY tools/browser/seccomp.playwright-1.56.1.json tools/browser/LICENSE.playwright ./
RUN chmod -R a-w /opt/verifier && mkdir /opt/readonly-probe && chown 1000:1000 /opt/readonly-probe && chmod 700 /opt/readonly-probe
USER 1000:1000
ENV HOME=/tmp TMPDIR=/tmp
ENTRYPOINT ["node", "/opt/verifier/capability_browser_worker.cjs"]
````
