# tools/daytona/capability-snapshot.Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/capability-snapshot.Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L58。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2941`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/capability-snapshot.Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7106bd648e7aa1047418264572971a72b2c36ce66100dc28af40bebdaef86f4d"} -->
````dockerfile
# tools/daytona/capability-snapshot.Dockerfile
# syntax=docker/dockerfile:1
# No candidate source enters this build. Runtime dependencies are built at their
# final paths; the application keeps /tmp noexec and never installs executable code.
ARG UV_IMAGE
ARG NODE_IMAGE
ARG SANDBOX_IMAGE
FROM ${UV_IMAGE} AS uv
FROM ${NODE_IMAGE} AS node
FROM ${SANDBOX_IMAGE} AS foundation
USER root
RUN apt-get update && apt-get install -y --no-install-recommends libseccomp2 procps python3 \
    && rm -rf /var/lib/apt/lists/*
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
    UV_PYTHON_PREFERENCE=only-managed UV_LINK_MODE=copy UV_NO_PROGRESS=1 \
    PYTHONUTF8=1 DO_NOT_TRACK=1
# Managed interpreter installation is trusted, and never writable by the builder.
RUN uv python install 3.14.7 \
    && mkdir -p /opt/rnd/bin /opt/rnd/control /opt/rnd/runtime /opt/rnd/browsers \
    && chown daytona:daytona /opt/rnd/browsers \
    && ln -s "$(uv python find 3.14.7)" /opt/rnd/bin/python-build
COPY dependency-image.py dependency-build.py /opt/rnd/bin/
USER daytona
RUN /opt/rnd/browser/node_modules/.bin/playwright install chromium

FROM foundation AS dependency-builder
USER 0:0
RUN mkdir -p /opt/rnd/runtime/python-basic/.venv /opt/rnd/build \
    && chown daytona:daytona /opt/rnd/runtime/python-basic/.venv /opt/rnd/build
COPY pyproject.toml uv.lock /opt/rnd/runtime/python-basic/
COPY dependency-inputs.json /opt/rnd/build-inputs.json
USER daytona
WORKDIR /opt/rnd/runtime/python-basic
RUN /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py install --basic --project /opt/rnd/runtime/python-basic \
    && /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py collect \
        --inputs /opt/rnd/build-inputs.json --output /opt/rnd/build/runtime-inputs.json

FROM foundation
USER 0:0
COPY --from=dependency-builder --chown=0:0 /opt/rnd/runtime/python-basic/ /opt/rnd/runtime/python-basic/
COPY --from=dependency-builder --chown=0:0 /opt/rnd/build/runtime-inputs.json /opt/rnd/runtime-inputs.json
# Data-only traversal validates all links/hardlinks before no-follow sealing.
RUN chmod 0755 /opt/rnd /opt/rnd/control /opt/rnd/runtime \
    && /usr/bin/python3 -I -S /opt/rnd/bin/dependency-image.py create \
        --profile python-basic --inputs /opt/rnd/runtime-inputs.json
ENV RND_OFFLINE_TOOLS=1 UV_OFFLINE=1 COREPACK_ENABLE_NETWORK=0
ENTRYPOINT []
CMD []
WORKDIR /opt/rnd/control
USER 0:0
````
