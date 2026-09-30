# Local object store; exact source revision is verified and exported by daytona_build.
FROM golang:1.24.8-bookworm AS builder
ENV CGO_ENABLED=0 GOTOOLCHAIN=local GOTELEMETRY=off GOMAXPROCS=2
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -mod=readonly -buildvcs=false -trimpath -p 2 \
    -ldflags "-s -w -X github.com/minio/minio/cmd.Version=2025-10-15T17:29:55Z -X github.com/minio/minio/cmd.ReleaseTag=RELEASE.2025-10-15T17-29-55Z -X github.com/minio/minio/cmd.CommitID=9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a" \
    -o /out/minio .
FROM alpine:3.22.2
RUN apk add --no-cache ca-certificates curl && mkdir -p /data
COPY --from=builder /out/minio /usr/local/bin/minio
COPY --from=builder /src/LICENSE /src/go.mod /src/go.sum /src/source.tar /usr/share/minio/
ENV MINIO_UPDATE=off DO_NOT_TRACK=1
EXPOSE 9000 9001
VOLUME ["/data"]
HEALTHCHECK CMD ["curl", "-f", "http://localhost:9000/minio/health/live"]
ENTRYPOINT ["/usr/local/bin/minio"]
CMD ["server", "/data", "--console-address", ":9001"]
