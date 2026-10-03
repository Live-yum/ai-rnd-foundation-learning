# tools/daytona/capability-snapshot.Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/capability-snapshot.Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L40。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1593`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/capability-snapshot.Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "97c9f52c3e3a395f9d2a5a29924ac7f8c4c4787e782693e10029fc726507971e"} -->
````dockerfile
# tools/daytona/capability-snapshot.Dockerfile
# Build dependencies are downloaded here, not while executing generated code.
ARG UV_IMAGE
ARG NODE_IMAGE
ARG SANDBOX_IMAGE
FROM ${UV_IMAGE} AS uv
FROM ${NODE_IMAGE} AS node
FROM ${SANDBOX_IMAGE}
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

ENTRYPOINT []
CMD []
# The normal Daytona daemon uses this declared image identity. The application
# guard independently drops to UID/GID 20000 with no capabilities or new privileges.
USER 0:0
RUN mkdir -p /opt/rnd/control && chown 0:0 /opt/rnd /opt/rnd/control \
    && chmod 0755 /opt/rnd /opt/rnd/control
WORKDIR /opt/rnd/control
USER 0:0
````
