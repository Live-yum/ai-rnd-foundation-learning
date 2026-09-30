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
