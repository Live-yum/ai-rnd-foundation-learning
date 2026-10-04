# tools/browser/SECCOMP-REVIEW.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/browser/SECCOMP-REVIEW.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L46。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2785`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/browser/SECCOMP-REVIEW.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0bcde334c78e5ea7a5082b11a8b25a0419e993fa0b36fd22d59d02b3cab3976d"} -->
````markdown
<!-- tools/browser/SECCOMP-REVIEW.md -->
# Prepared profile; not activated

`seccomp.playwright-1.56.1.json` is an unmodified, review-only copy of
[Microsoft Playwright v1.56.1's Docker profile](https://raw.githubusercontent.com/microsoft/playwright/v1.56.1/utils/docker/seccomp_profile.json).
Its SHA-256 is `cc3e61cabda6bbc1e53e54d27ba4d55a9d3be829b6dd1a596f4a7b31b1cc7849`.
The upstream Apache 2.0 license is preserved in `LICENSE.playwright`.

## Exact namespace rule

Relative to the historical default profile embedded in this upstream file, its
first rule adds unconditional `SCMP_ACT_ALLOW` for exactly `clone`, `setns`, and
`unshare`, with no argument predicates. The purpose is to let non-root Chromium
create its own user/PID/network namespaces. It does not grant host capabilities,
host namespace descriptors, host mounts, or permission to join a host namespace.
The kernel's user-namespace ownership/capability rules still apply.

This is **not** a claim that those three calls are the only differences from the
installed Docker engine's modern default. The full historical profile also has
its own syscall list, architecture mappings and capability-dependent rules. For
example, it allows io_uring calls and a kernel-dependent ptrace rule, omits an
explicit clone3/ENOSYS fallback rule, and conditions chroot on CAP_SYS_CHROOT.
Those details require an explicit current-engine comparison before activation,
especially with this worker's `cap-drop=ALL` policy. Do not replace the default
profile with this file merely to make a launch error disappear.

## Activation requirements

The current launcher does **not** select this profile. It retains Docker's
default seccomp policy, no-new-privileges, all capabilities dropped, network none,
private PID/IPC/cgroup namespaces and Chromium's OS sandbox. Inspection rejects
an unexpected seccomp option. No host AppArmor, sysctl or Docker-daemon setting is
changed, and there is no `--no-sandbox` fallback.

Before adding an explicit per-worker profile selector, review the exact syscall
delta against the selected engine, narrow unnecessary allowances, and establish
actual Chromium user-namespace startup plus negative escape/resource/network
probes under that exact policy. A host which denies user namespaces remains
unsupported; the code does not weaken host policy to admit it.

The prepared file is copied into the immutable worker image, hashed directly
from the stopped container, and included in the v2 browser receipt's host-source
and image-source bindings. Editing the profile, introducing a policy selector or
changing its enforcement therefore invalidates existing evidence. A future
active policy must also be identified explicitly in the receipt and checked
against the actual container SecurityOpt; old Docker-default receipts must not
authorize it.
````
