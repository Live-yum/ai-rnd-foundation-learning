# tools/daytona/Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L27。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1245`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a0eb4b1ab7d645a830884c5530807b21537240c2f8acd724844efd797b04b31c"} -->
````dockerfile
# tools/daytona/Dockerfile
# Build dependencies are downloaded here, not while executing generated code.
FROM ghcr.io/astral-sh/uv:0.12.20 AS uv
FROM node:22.23.2-bookworm-slim AS node
FROM daytonaio/sandbox:0.5.0-slim
USER root
COPY --from=uv /uv /uvx /usr/local/bin/
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/rnd/browsers \
    PRODUCT_VERIFY_PLAYWRIGHT=/opt/rnd/browser/node_modules/playwright
RUN npm install --prefix /opt/rnd/browser --no-audit --no-fund --package-lock=false playwright@1.56.1 \
    && /opt/rnd/browser/node_modules/.bin/playwright install-deps chromium
ENV UV_CACHE_DIR=/opt/rnd/uv-cache \
    UV_PYTHON_INSTALL_DIR=/opt/rnd/python \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_LINK_MODE=copy \
    UV_NO_PROGRESS=1 \
    PYTHONUTF8=1 \
    DO_NOT_TRACK=1
WORKDIR /opt/rnd/prewarm
COPY pyproject.toml uv.lock ./
RUN uv python install 3.14.7 && uv sync --locked --no-dev --python 3.14.7 \
    && rm -rf .venv && chown -R daytona:daytona /opt/rnd
USER daytona
RUN /opt/rnd/browser/node_modules/.bin/playwright install chromium
WORKDIR /home/daytona
````
