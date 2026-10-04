# tools/daytona/capability-native-snapshot.Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/capability-native-snapshot.Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L48。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2658`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/capability-native-snapshot.Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "99c6c41dfa06f707189950af22ae26cdbe6e6531188952214d8c5b2cc7bd5180"} -->
````dockerfile
# tools/daytona/capability-native-snapshot.Dockerfile
# Dedicated root-control base, supplied as the locally verified registry digest and image ID.
# Dependency preparation only: no generated application/control code or hooks run here.
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
USER 0:0
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg git redis-server libseccomp2 procps \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl --fail --silent --show-error https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
    && . /etc/os-release \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends postgresql-17 \
    && rm -rf /var/lib/apt/lists/*
RUN /usr/local/bin/node /usr/local/lib/node_modules/npm/bin/npm-cli.js install \
        --global --prefix /usr/local --no-audit --no-fund pnpm@9.15.3 \
    && mkdir -p /opt/rnd/harness /opt/rnd/prewarm /opt/rnd/pnpm-store \
    && chown -R daytona:daytona /opt/rnd/harness /opt/rnd/prewarm /opt/rnd/pnpm-store
ENV PATH=/usr/lib/postgresql/17/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    CI=true HUSKY=0
COPY --chown=daytona:daytona harness/ /opt/rnd/harness/
COPY --chown=daytona:daytona product/ /opt/rnd/prewarm/product/
USER daytona
RUN test "$(pnpm --version)" = "9.15.3" && postgres --version | grep 'PostgreSQL) 17\.'
WORKDIR /opt/rnd/harness
RUN uv sync --locked --all-extras --no-install-project --python 3.14.7
WORKDIR /opt/rnd/prewarm/product/deployment
RUN uv sync --locked --all-extras --no-install-project --python 3.14.7
WORKDIR /opt/rnd/prewarm/product/backend
RUN uv sync --locked --all-extras --no-install-project --python 3.14.7
WORKDIR /opt/rnd/prewarm/product/frontend/web
# No .npmrc, pnpmfile, Vite configuration, source or workspace scripts are copied.
RUN pnpm fetch --frozen-lockfile --ignore-scripts --store-dir /opt/rnd/pnpm-store \
    && pnpm install --frozen-lockfile --offline --ignore-scripts \
        --store-dir /opt/rnd/pnpm-store \
    && test -f node_modules/vue/package.json \
    && test -f node_modules/vite/package.json \
    && test -f node_modules/vue-tsc/package.json
USER 0:0
RUN rm -rf /opt/rnd/prewarm \
    && chown -R 0:0 /opt/rnd \
    && chmod -R a+rX /opt/rnd \
    && mkdir -p /opt/rnd/control && chmod 0755 /opt/rnd /opt/rnd/control
ENV RND_OFFLINE_TOOLS=1 UV_OFFLINE=1 COREPACK_ENABLE_NETWORK=0
ENTRYPOINT []
CMD []
WORKDIR /opt/rnd/control
USER 0:0
````
