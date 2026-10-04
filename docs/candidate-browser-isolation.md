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
