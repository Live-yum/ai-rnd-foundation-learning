# Official v0.190.0 runner (including daemon); SHA256 checked BEFORE docker build.
# The upstream runner runtime also uses Docker-in-Docker. Development use only.
FROM docker:28.5.2-dind-alpine3.22 AS runner
RUN apk update && apk upgrade --no-cache openssl pcre2 \
    && apk add --no-cache curl rsync
WORKDIR /usr/local/bin
COPY --chmod=0755 runner-amd64 daytona-runner
RUN mkdir -p /etc/docker && \
    printf '%s\n' '{"insecure-registries": ["registry:6000"]}' > /etc/docker/daemon.json
ENV DO_NOT_TRACK=1 OTEL_SDK_DISABLED=true
HEALTHCHECK CMD ["curl", "-f", "http://localhost:3003/"]
ENTRYPOINT ["sh", "-c", "/usr/local/bin/dockerd-entrypoint.sh & exec daytona-runner"]
