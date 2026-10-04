# docs/candidate-browser-isolation.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本教材正文的源文件。** 上文正文就是这些源文件拼接后的内容。它们也收录在附录中，使从教材还原出的项目能再次生成逐字一致的完整教材，而不是只有一次性的代码快照。

**对应关系：** scripts/build_handbook.py的GUIDES → 正文 → 完整源码附录。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/candidate-browser-isolation.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L77。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4891`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/candidate-browser-isolation.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e4c3a9e9e56c77806d0dd74cf2c21985e5625f40755a77ef10b20f03dc8275fe"} -->
````markdown
<!-- docs/candidate-browser-isolation.md -->
# Candidate browser isolation (experimental, fail closed)

Custom-source browser execution must use `run_isolated_browser`, never the
legacy host-browser fixture runner. The custom execution gate remains disabled
until the exact verifier sources and immutable browser image have live evidence.
A successful policy unit test or a Docker command line is not certification.
Before execution or certification, bounded read-only Docker copies from the
stopped worker verify the actual driver, relay, network probe and Dockerfile
bytes against current source hashes. An old image cannot receive a new-source
certificate merely because its older tests still pass.

## Boundary

The controller creates a dedicated container from an explicitly configured
`sha256:` image ID. Before starting it, the controller inspects its actual image,
identity, namespaces, read-only filesystem, dropped capabilities, resource limits,
mounts and network mode. It uses no host mounts, published ports, host IPC/PID
namespace, host security changes or privileged container. The browser retains
Chromium's OS sandbox; an unavailable sandbox is a blocking failure.

The entire browser worker has `network=none`, 1 CPU, 768 MiB memory with no swap
headroom, 128 PIDs, a 128 MiB non-executable `/tmp`, and 64 MiB private shared
memory. Profile data and browser descendants disappear on forced container
removal. The controller removes the complete container on success, invalid
output, timeout, browser error and resource abuse. An unconfirmed removal fails
acceptance.

A trusted Node HTTP server listens only on container loopback. It relays HTTP
requests as framed stdio to the controller, which forwards only relative paths
to the already validated private application origin. The preview token never
enters the browser container. No redirects, CONNECT, upgrades, compression or
candidate-supplied host/proxy/preview-token headers are accepted. WebSocket,
WebRTC and DNS cannot create an outbound network path from `network=none`.

Budgets: 4 MiB per request/response body, 32 MiB total transferred bodies,
256 requests, 8 worker-side concurrent requests, bounded headers and frames,
5-second HTTP timeouts and at most 180 seconds for the complete worker. Capture
substitution is checked before string construction, and cumulative JSON size is
proved before encoding or container creation. The browser contract limit also
bounds controller-side preparation, including repeated captures. Candidate
JS cannot write trusted driver stdout or replace its request-bound, source-hash
bound assertions with a JSON completion claim. Candidate browser code is still
untrusted; the image and controller are trusted, and the OS sandbox is required.

The HTTP verifier separately limits retained capture values to 16 KiB each and
all saved scenario state to 1,000,000 accounted bytes, including conservative
dictionary-entry overhead. Replacing a variable credits its previous size;
ordinary reuse does not consume the budget repeatedly. Non-finite numbers,
oversized values and over-budget interpolation fail before retention or request
construction. These limits reject excessive data rather than silently truncating it.

## Real proof

Build `tools/browser/Dockerfile` with Docker, select the resulting immutable image
ID in `CAPABILITY_BROWSER_IMAGE`, then run:

    uv run python -m scripts.ci_capability_browser_isolation

The dedicated GitHub Actions workflow runs the same command. Its bounded report
records live kernel cgroup values, TCP/UDP denial, read-only root, tmpfs/PID exhaustion and an actual cgroup OOM kill; then requires a real browser click/assertion, JavaScript-error
rejection, busy-loop termination and no surviving browser containers. It does
not change host AppArmor, sysctls, seccomp or credentials to make a test pass.
Network proof requires a loopback-only namespace, no IPv4 routes, specifically
ENETUNREACH for non-local TCP/UDP and successful local TCP. A refused connection
or timeout is not isolation evidence. Read-only root proof requires EROFS on an
otherwise writable worker-owned directory; a generic permission error fails.
The runtime probe also requires UID/GID 1000, no-new-privileges, active seccomp
filter mode and zero inheritable/permitted/effective/bounding/ambient capabilities.

The image currently uses the standard Docker security profile. Whether the
runner permits Chromium's user namespaces is deliberately established by live
CI rather than assumed; failure keeps arbitrary-source execution unavailable.
An unmodified pinned upstream profile is prepared for review only; see
`tools/browser/SECCOMP-REVIEW.md` for its exact namespace rule and activation
requirements. It is image/receipt-bound but is not automatically selected.
The report is only one prerequisite: application sandbox/network/database
acceptance and exact source/image binding remain mandatory separately.
````
