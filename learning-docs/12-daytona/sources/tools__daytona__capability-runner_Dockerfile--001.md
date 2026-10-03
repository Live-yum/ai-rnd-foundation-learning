# tools/daytona/capability-runner.Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/capability-runner.Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L59。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3651`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/capability-runner.Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6914b11fecb2d7ea54b5141f5900c5ebf7e2dedeb8fd13a1da1d8c482cea0829"} -->
````dockerfile
# tools/daytona/capability-runner.Dockerfile
# Owned fixed-application profile, based on Daytona's AGPL-3.0 source at the
# exact revision checked by scripts.daytona_capability_profile. Build graph:
# daemon + its pinned terminal assets, real computer-use plugin, then Runner.
# All FROM arguments are official, digest-locked images supplied by the helper.
ARG GO_IMAGE
ARG BUILD_IMAGE
ARG DOCKER_IMAGE
ARG RUNTIME_IMAGE
FROM ${GO_IMAGE} AS go-toolchain
FROM ${BUILD_IMAGE} AS builder
COPY --from=go-toolchain /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:${PATH}" GOTOOLCHAIN=local GOTELEMETRY=off \
    GOOS=linux GOARCH=amd64 GOMAXPROCS=2 GOFLAGS="-mod=readonly -buildvcs=false -trimpath -p=2"
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates gcc libc6-dev libx11-dev libxtst-dev libpng-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . .
# Keep upstream's complete workspace and every go.mod/go.sum unchanged. The
# upstream tree omits go.work.sum; the helper seeds it from committed module sums.
# Go may add checksums for the pinned workspace graph, captured with the source.
RUN mkdir -p apps/runner/pkg/daemon/static /out \
    && sha256sum go.work $(find apps libs -name go.mod -o -name go.sum | sort) > /tmp/go-inputs.sha256 \
    && CGO_ENABLED=0 go build -ldflags='-X github.com/daytonaio/daemon/internal.Version=0.190.0' \
        -o apps/runner/pkg/daemon/static/daemon-amd64 ./apps/daemon/cmd/daemon \
    && CGO_ENABLED=1 go build -o apps/runner/pkg/daemon/static/daytona-computer-use ./libs/computer-use \
    && CGO_ENABLED=0 go build -ldflags='-X github.com/daytonaio/runner/internal.Version=0.190.0' \
        -o /out/daytona-runner ./apps/runner/cmd/runner \
    && sha256sum -c /tmp/go-inputs.sha256 \
    && go version -m /out/daytona-runner > /out/runner-build-info.txt \
    && sha256sum /out/daytona-runner apps/runner/pkg/daemon/static/daemon-amd64 \
        apps/runner/pkg/daemon/static/daytona-computer-use > /out/binaries.sha256 \
    && tar --exclude='./apps/runner/pkg/daemon/static/daemon-amd64' \
        --exclude='./apps/runner/pkg/daemon/static/daytona-computer-use' \
        -cf /out/source.tar .
FROM ${DOCKER_IMAGE} AS docker-tools
FROM ${RUNTIME_IMAGE} AS runner
# Retain the ordinary Runner's glibc-compatible runtime and local DinD startup.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl rsync iptables iproute2 kmod procps openssl xz-utils \
    && rm -rf /var/lib/apt/lists/*
COPY --from=docker-tools /usr/local/bin/ /usr/local/bin/
WORKDIR /usr/local/bin
COPY --from=builder --chmod=0755 /out/daytona-runner /usr/local/bin/daytona-runner
COPY --chmod=0755 capability-build/runner-entry.sh /usr/local/bin/rnd-runner-entry.sh
COPY --from=builder /out/source.tar /out/runner-build-info.txt /out/binaries.sha256 /usr/share/daytona-profile/
COPY LICENSE capability-build/NOTICE /usr/share/daytona-profile/
RUN set +e; API_PORT=invalid /usr/local/bin/daytona-runner >/tmp/runner-smoke.log 2>&1; \
    result=$?; set -e; cat /tmp/runner-smoke.log; \
    test "$result" = 2 && grep -q 'Failed to get config' /tmp/runner-smoke.log \
    && rm /tmp/runner-smoke.log
RUN mkdir -p /etc/docker && \
    printf '%s\n' '{"insecure-registries": ["registry:6000"]}' > /etc/docker/daemon.json
ENV DO_NOT_TRACK=1 OTEL_SDK_DISABLED=true DOCKER_HOST=unix:///var/run/docker.sock \
    USE_SNAPSHOT_ENTRYPOINT=false
VOLUME ["/var/lib/docker"]
HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=12 \
    CMD docker info >/dev/null && curl -f http://localhost:3003/
ENTRYPOINT ["/usr/local/bin/dind", "/usr/local/bin/rnd-runner-entry.sh"]
````
