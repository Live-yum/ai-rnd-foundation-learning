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
