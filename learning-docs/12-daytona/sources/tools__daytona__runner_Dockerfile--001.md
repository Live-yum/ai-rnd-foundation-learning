# tools/daytona/runner.Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Runner服务镜像。** 以固定Docker-in-Docker运行环境装入已经验证大小和SHA256的v0.190.0 Runner发布文件；入口同时启动本机Docker daemon与Runner。私有registry登记为本机不安全HTTP仓库，不指向公网。它不是产品快照。

**对应关系：** daytona_build.download_runner → build_exported → daytona_local.images/up → Runner管理本机沙箱。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/runner.Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L23。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1400`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/runner.Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2a87067c4e5c3305f95821a5682eb25627d034cfed67011132b87f210b677f1b"} -->
````dockerfile
# tools/daytona/runner.Dockerfile
# Same verified v0.190.0 release binary, with a glibc-compatible local runtime.
FROM docker:28.5.2-dind-alpine3.22 AS docker-tools
FROM debian:trixie-slim AS runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl rsync iptables iproute2 kmod procps openssl xz-utils \
    && rm -rf /var/lib/apt/lists/*
# Docker's static binaries and DinD initialization script; no hosted Docker daemon.
COPY --from=docker-tools /usr/local/bin/ /usr/local/bin/
WORKDIR /usr/local/bin
COPY --chmod=0755 runner-amd64 daytona-runner
COPY --chmod=0755 runner-entry.sh /usr/local/bin/rnd-runner-entry.sh
# Prove the executable reaches its own config parser, without a running daemon.
RUN set +e; API_PORT=invalid /usr/local/bin/daytona-runner >/tmp/runner-smoke.log 2>&1; \
    result=$?; set -e; cat /tmp/runner-smoke.log; \
    test "$result" = 2 && grep -q 'Failed to get config' /tmp/runner-smoke.log \
    && rm /tmp/runner-smoke.log
RUN mkdir -p /etc/docker && \
    printf '%s\n' '{"insecure-registries": ["registry:6000"]}' > /etc/docker/daemon.json
ENV DO_NOT_TRACK=1 OTEL_SDK_DISABLED=true DOCKER_HOST=unix:///var/run/docker.sock
VOLUME ["/var/lib/docker"]
HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=12 \
    CMD docker info >/dev/null && curl -f http://localhost:3003/
ENTRYPOINT ["/usr/local/bin/dind", "/usr/local/bin/rnd-runner-entry.sh"]
````
