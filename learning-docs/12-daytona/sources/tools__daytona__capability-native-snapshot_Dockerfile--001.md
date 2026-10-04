# tools/daytona/capability-native-snapshot.Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/capability-native-snapshot.Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L82。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4986`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/capability-native-snapshot.Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e15accbd38f1f929a6499d767868d190c95b6d1e9bb290849ac0dc1fb1d5f540"} -->
````dockerfile
# tools/daytona/capability-native-snapshot.Dockerfile
# syntax=docker/dockerfile:1
# Dedicated root-control base, supplied as verified registry digest and image ID.
ARG BASE_IMAGE
ARG RUST_IMAGE
FROM ${RUST_IMAGE} AS rust
FROM ${BASE_IMAGE} AS native-system
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
        --global --prefix /usr/local --no-audit --no-fund pnpm@9.15.3
ENV PATH=/usr/lib/postgresql/17/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    CI=true HUSKY=0
COPY dependency-image.py dependency-build.py dependency-build.lock.json /opt/rnd/bin/

# Registry source builds cannot reach final controller files, credentials or host
# mounts. Root prepares only OS/compiler inputs; ALL dependency code runs daytona.
FROM native-system AS dependency-builder
USER 0:0
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/rnd/harness /opt/rnd/build /opt/rnd/build-tools /opt/rnd/runtime/fastapiadmin/backend \
        /opt/rnd/runtime/fastapiadmin/frontend /opt/rnd/pnpm-store \
    && chown daytona:daytona /opt/rnd/build /opt/rnd/build-tools
COPY --from=rust /usr/local/cargo /usr/local/cargo
COPY --from=rust /usr/local/rustup /usr/local/rustup
ENV RUSTUP_HOME=/usr/local/rustup CARGO_HOME=/opt/rnd/build/cargo \
    UV_OFFLINE=0 PATH=/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin
COPY harness/ /opt/rnd/harness/
COPY product/backend/ /opt/rnd/runtime/fastapiadmin/backend/
COPY product/frontend/web/ /opt/rnd/runtime/fastapiadmin/frontend/
COPY dependency-inputs.json /opt/rnd/build-inputs.json
USER daytona
RUN /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py fetch \
    --lock /opt/rnd/bin/dependency-build.lock.json --project /opt/rnd/runtime/fastapiadmin/backend
# Seal the hash-verified build tools as data, without following dependency links.
USER 0:0
RUN /usr/bin/python3 -I -S /opt/rnd/bin/dependency-image.py seal-build-tools --profile fastapiadmin
USER daytona
# Cargo.lock and Python build tools are hash-bound before network is removed.
# No ABI override, lock rewrite, package omission or online build fallback.
RUN --network=none /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py build-sources
# The source build container has exited. Only now create fresh writable install
# destinations; source backends never had write access to descriptors or venvs.
USER 0:0
RUN mkdir /opt/rnd/runtime/fastapiadmin/backend/.venv /opt/rnd/harness/.venv \
    && chown daytona:daytona /opt/rnd/runtime/fastapiadmin/backend/.venv /opt/rnd/harness/.venv \
        /opt/rnd/runtime/fastapiadmin/frontend /opt/rnd/pnpm-store
USER daytona
RUN /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py install --project /opt/rnd/runtime/fastapiadmin/backend \
    && /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py install --harness --project /opt/rnd/harness
WORKDIR /opt/rnd/runtime/fastapiadmin/frontend
RUN test "$(pnpm --version)" = "9.15.3" \
    && pnpm fetch --frozen-lockfile --ignore-scripts --store-dir /opt/rnd/pnpm-store \
    && pnpm install --frozen-lockfile --offline --ignore-scripts --package-import-method=copy \
        --store-dir /opt/rnd/pnpm-store \
    && test -f node_modules/vue/package.json && test -f node_modules/vite/package.json \
    && test -f node_modules/vue-tsc/package.json
RUN /opt/rnd/bin/python-build -I -S /opt/rnd/bin/dependency-build.py collect --native \
    --inputs /opt/rnd/build-inputs.json --output /opt/rnd/build/runtime-inputs.json

FROM native-system
USER 0:0
COPY --from=dependency-builder --chown=0:0 /opt/rnd/runtime/fastapiadmin/ /opt/rnd/runtime/fastapiadmin/
COPY --from=dependency-builder --chown=0:0 /opt/rnd/harness/ /opt/rnd/harness/
COPY --from=dependency-builder --chown=0:0 /opt/rnd/build/runtime-inputs.json /opt/rnd/runtime-inputs.json
# Never recursively chown/chmod through dependency-created links. Validation and
# sealing use O_NOFOLLOW directory descriptors and reject links outside the graph.
RUN /usr/bin/python3 -I -S /opt/rnd/bin/dependency-image.py create \
        --profile fastapiadmin --inputs /opt/rnd/runtime-inputs.json
ENV RND_OFFLINE_TOOLS=1 UV_OFFLINE=1 COREPACK_ENABLE_NETWORK=0
ENTRYPOINT []
CMD []
WORKDIR /opt/rnd/control
USER 0:0
````
