# tools/browser/review-only-v2/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/browser/review-only-v2/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L108。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6491`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/browser/review-only-v2/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ac7d3070874970f00f1a4743571d34d1da881d658d43540bcdbe8ca4a68d222c"} -->
````markdown
<!-- tools/browser/review-only-v2/README.md -->
# Actions-only v2: native-amd64 Chromium namespace profile

The exact policy below has been reviewed and approved for disposable, offline
Actions browser workers only. `capability_browser_policy` requires an explicit
fixed-hash selector, approved repository/workflow and observed native-amd64
Docker 28.0.4 target. Ordinary callers retain their existing default profile.
This configuration is not a live certification; all positive and adversarial
checks must pass on the published commit before candidate admission.

## Provenance and exact changes

The baseline remains the byte-verified Docker 28.0.4 profile and license in
`../review-only/`. Its pinned upstream commit/source hashes and the independently
verified Chromium 141.0.7390.37 call sites are retained in that directory's
`proposal-manifest.json`. The baseline file itself is unchanged.

Candidate SHA-256:
`9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f`

`review_profile.build_profile` is the reproducible exact transformation:

1. Retain only the native `SCMP_ARCH_X86_64` ABI, without x86/x32 compatibility
   ABIs. Remove `socketcall` from the broad allow list. The shipped Node and
   Chromium target is native amd64; compatibility executables are unsupported.
2. Remove the baseline's unrestricted `socketpair` entry and its full-word
   `socket != 40` allowance. For **each** of `socket` and `socketpair`, 32 bit-mask
   allow clauses express exactly `(arg0 & 0xffffffff) != 40`. Any high-word variant
   of AF_VSOCK therefore reaches default EPERM. All non-VSOCK family values retain
   their baseline allowance, which is not a promise of kernel socket availability.
3. Append the same five source-justified Chromium allowances as v1:
   - clone arg0 EQ `0x10000011`: NEWUSER | SIGCHLD
   - clone arg0 EQ `0x70000011`: NEWUSER | NEWPID | NEWNET | SIGCHLD
   - clone arg0 EQ `0x20000011`: NEWPID | SIGCHLD
   - unshare arg0 EQ `0x10000000`: NEWUSER only
   - chroot, with its pathname not filterable by classic seccomp

The new clauses are restricted to Moby's amd64 host selector and exclude initial
CAP_SYS_ADMIN. Every other baseline rule/property is preserved. In particular,
clone3's ENOSYS fallback, io_uring denial, and setns/mount/pivot_root restrictions
remain unchanged for the intended empty initial capability bounding set. There
is no unrestricted clone, unshare or setns permission.

The 64 transport clauses are intentionally explicit: Moby/libseccomp lacks a
masked-NE argument operator. Simply appending a deny that overlaps the baseline
allow is unsafe; offline exported-BPF evaluation showed the overlapping allow can
win. Removing that overlap and using the complement of low-32 equality makes the
transport cases disjoint. Socketpair is covered rather than relying on a current
kernel's lack of VSOCK socketpair support.

## Fail-closed target contract

Supported proposal target: Docker server 28.0.4, daemon and image architecture
amd64, native process ABI x86_64, and an empty initial capability bounding set.
The runtime selector observes Docker server, image and controller architecture,
engine/kernel/runtime versions and host runc/libseccomp version. Before start,
inspection must match the exact inline profile and Docker AppArmor confinement.
The trusted live probe checks Node and Chromium ELF ABI, pinned browser versions,
all zero capability sets, NNP and resource/network limits. A new v3 receipt binds
the observed runtime and policy to source/image hashes. Unknown targets fail.
The offline helper remains an export-only model, separate from live execution.

## Offline checks and limits

`review_profile.compile_bpf` uses the installed system libseccomp to **export** a
filter into a temporary file; it never loads a filter, starts a container or
changes process/kernel policy. It models the declared native-amd64,
empty-capability, kernel-6.17 review conditions. A bounded classic-BPF interpreter
checks the exported instructions against synthetic syscall inputs:

- socket and socketpair family 40 with canonical and high-word/truncated variants
- x86 socketcall/direct-socket and x32 syscall-bit attempts, which fail closed
- other audit architectures, exact allowed clone/unshare cases, extra flags and
  alternative signals, retained clone3 ENOSYS, and io_uring/setns/mount denial
- non-VSOCK family preservation and a symbol-restricted compiler interface

These are stronger than testing the JSON evaluator alone, but are **not kernel,
AppArmor, Docker/runc-compiler or live network-containment evidence**. The CI
runtime may use a different compiler/version. Windows or missing-libseccomp test
runs cannot establish these results; `RND_REQUIRE_SECCOMP_BPF=1` makes absence a
failure for the supported offline review job. A real activation still needs actual
runtime/kernel/compiler provenance and positive/adversarial execution evidence.

## Risk and maintained containment

User-namespace creation exposes additional kernel attack surface and grants
namespace-scoped capabilities to child namespaces. NNP does not prevent that.
The calls are available to compromised code too, not just Chromium. `chroot`
requires CAP_SYS_CHROOT in the caller's user namespace; the initial worker lacks
it, but a child user namespace can possess it. Its pathname cannot be constrained
by this policy, and chroot alone is not a jail. The native-only ABI restriction
reduces compatibility surface but does not establish freedom from kernel bugs.

NNP, cap-drop=ALL, non-root UID, network-none, read-only root, no host mounts,
ports or devices, private namespaces, resource limits and Chromium's own sandbox
remain mandatory and unchanged. The JSON cannot enforce those outer settings.
AppArmor may independently block launch; this proposal does not disable or alter
it. Never broaden permissions, switch to host Chrome, add capabilities or turn
off Chromium's sandbox when a check fails.

## Required live evidence

Independent review of this exact delta/hash and helper; explicit per-action user
approval; reviewed target selection/effective-policy inspection; receipts bound
to exact policy and actual engine/kernel/image/compiler provenance; and fresh
positive/adversarial browser, network (including ABI/argument-width cases),
filesystem, namespace, resource and cleanup checks are all required. Unknown or
failed evidence must block candidate admission. Any additional permission needs
a separate decision. Approval is limited to the documented disposable Actions scope.
````
