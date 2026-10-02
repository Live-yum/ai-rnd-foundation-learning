# tools/daytona/matrix.Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/matrix.Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L51。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2994`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/matrix.Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0a496fffe70635893cde06717c70cf1f13bfc98c5cb144825d9b4d597b7811ea"} -->
````dockerfile
# tools/daytona/matrix.Dockerfile
# Explicit local image preparation. Generated code is executed later without egress.
FROM ghcr.io/astral-sh/uv:0.12.20 AS uv
FROM node:22.23.2-bookworm-slim AS node
FROM eclipse-temurin:17-jdk-jammy AS java
FROM daytonaio/sandbox:0.5.0-slim
USER root
COPY --from=java /opt/java/openjdk /opt/java/openjdk
COPY --from=uv /uv /uvx /usr/local/bin/
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && apt-get update && apt-get install -y --no-install-recommends ca-certificates curl gnupg git redis-server maven \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl --fail --silent --show-error https://www.postgresql.org/media/keys/ACCC4CF8.asc -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
    && . /etc/os-release && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends postgresql-17 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/rnd/harness /opt/rnd/browser /opt/rnd/prewarm \
    && chown -R daytona:daytona /opt/rnd
ARG PNPM_VERSION=9.15.3
# The base image has its own NVM Node/npm on PATH. Install into the copied
# official Node prefix explicitly so pnpm remains available after PATH is fixed.
RUN /usr/local/bin/node /usr/local/lib/node_modules/npm/bin/npm-cli.js install \
    --global --prefix /usr/local --no-audit --no-fund pnpm@${PNPM_VERSION}
ENV UV_CACHE_DIR=/opt/rnd/uv-cache \
    UV_PYTHON_INSTALL_DIR=/opt/rnd/python \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_LINK_MODE=copy \
    UV_NO_PROGRESS=1 \
    PYTHONUTF8=1 \
    DO_NOT_TRACK=1 \
    PRODUCT_VERIFY_PLAYWRIGHT=/opt/rnd/browser/node_modules/playwright \
    PLAYWRIGHT_BROWSERS_PATH=/opt/rnd/browsers \
    JAVA_HOME=/opt/java/openjdk \
    PATH=/opt/java/openjdk/bin:/usr/lib/postgresql/17/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin
COPY --chown=daytona:daytona harness/ /opt/rnd/harness/
COPY --chown=daytona:daytona product/ /opt/rnd/prewarm/product/
COPY --chown=daytona:daytona profile.json warm.py /opt/rnd/
RUN npm install --prefix /opt/rnd/browser --no-audit --no-fund --package-lock=false playwright@1.56.1 \
    && /opt/rnd/browser/node_modules/.bin/playwright install-deps chromium \
    && chown -R daytona:daytona /opt/rnd
USER daytona
RUN command -v pnpm && test "$(pnpm --version)" = "${PNPM_VERSION}"
WORKDIR /opt/rnd/harness
RUN uv python install 3.14.7 \
    && uv sync --locked --all-extras --no-install-project --python 3.14.7 \
    && /opt/rnd/browser/node_modules/.bin/playwright install chromium \
    && .venv/bin/python /opt/rnd/warm.py \
    && rm -rf /opt/rnd/prewarm
ENV RND_OFFLINE_TOOLS=1 UV_OFFLINE=1 COREPACK_ENABLE_NETWORK=0
WORKDIR /home/daytona
````
