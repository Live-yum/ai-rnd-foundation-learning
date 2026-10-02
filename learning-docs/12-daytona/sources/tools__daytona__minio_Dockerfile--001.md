# tools/daytona/minio.Dockerfile · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机对象存储服务镜像。** 第一阶段在固定Go编译器中校验并编译固定MinIO源码；第二阶段只复制运行二进制、对应源码、许可证和依赖清单。数据写入独立持久卷；更新检查关闭，端点仅供本机开发网络使用。

**对应关系：** daytona_build.build_storage → images.lock → daytona_local.up → API/Runner使用本机S3存储。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/daytona/minio.Dockerfile`；**本文件共有 1 段**。本段覆盖源文件 L1–L20。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1025`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/minio.Dockerfile", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "865eb5018128db258c960c159e2fb65ca9cbab690ac72834c074f9ba3a469009"} -->
````dockerfile
# tools/daytona/minio.Dockerfile
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
````
