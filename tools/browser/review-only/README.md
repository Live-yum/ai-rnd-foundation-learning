# INACTIVE: Chromium 141 / Docker 28.0.4 seccomp proposal

This directory is a **review artifact, not an active runtime policy**. No launcher,
workflow, image-copy instruction, receipt gate, AppArmor profile, host setting,
capability bounding set, or browser argument selects it. Activation is **not
approved**. No container was launched with it and no live compatibility or
containment result is claimed. Static tests are not acceptance evidence.

## Provenance and scope

`moby-v28.0.4-default.json` preserves the UTF-8 payload retrieved from Moby
v28.0.4. `proposal-manifest.json` contains its commit-pinned upstream URL, SHA-256,
Chromium source URLs/hashes, candidate hash, and an append-only RFC 6902 JSON
patch. The original baseline JSON object and every baseline rule remain
unchanged. The Moby Apache 2.0 license is preserved in `LICENSE.moby`.

The current runner inventory lists Docker 28.0.4 and Linux 6.17.0-1022-azure:
https://github.com/actions/runner-images/blob/ubuntu24/20260927.320/images/ubuntu/Ubuntu2404-Readme.md
This is an image inventory, not an attestation of the active daemon or kernel.
Any activation review must re-establish actual versions and policy provenance.

The candidate is scoped to an **amd64 host**, Chromium 141.0.7390.37 (Playwright
1.56.1), all user/PID/network namespace features present, and an empty initial
container capability bounding set. Moby's `includes.arches` selects the host
architecture; it does **not** limit a rule to the native syscall ABI. The
unchanged amd64 archMap also includes x86/x32 compatibility ABIs. This inherited
compatibility surface requires review; this proposal makes no native-ABI-only
claim. Other host architectures receive no appended allowances.

## Exact delta: five appended rules, three syscall names

All new rules use SCMP_ACT_ALLOW, include only host arch `amd64`, and exclude
containers initially holding CAP_SYS_ADMIN. This condition is evaluated by Docker
at container creation; it is not a dynamic check of child namespace privileges.

| Syscall | Argument constraint | Decimal | Chromium source justification |
|---|---|---:|---|
| clone | arg0 EQ CLONE_NEWUSER \| SIGCHLD | 268435473 | Credentials::CanCreateProcessInNewUserNS availability probe |
| clone | arg0 EQ CLONE_NEWUSER \| CLONE_NEWPID \| CLONE_NEWNET \| SIGCHLD | 1879048209 | NamespaceSandbox default launch, with LaunchProcess adding SIGCHLD |
| clone | arg0 EQ CLONE_NEWPID \| SIGCHLD | 536870929 | NamespaceSandbox::ForkInNewPidNamespace |
| unshare | arg0 EQ CLONE_NEWUSER | 268435456 | Credentials availability probe and MoveToNewUserNS |
| chroot | No argument filter is possible for the pointed-to path | n/a | Credentials::DropFileSystemAccess / ChrootToSelfFdinfo |

No setns rule is added. No new namespace-flag masks or unrestricted clone/unshare
rule are added. No allowance is made for partially supported namespace launch
combinations. The original namespace-free clone rule already covers the
CLONE_FS/VM/VFORK/SETTLS helper used by Chromium's chroot implementation.

Source references, pinned to Chromium's version commit:
- [Credentials](https://github.com/chromium/chromium/blob/9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e/sandbox/linux/services/credentials.cc)
- [NamespaceSandbox](https://github.com/chromium/chromium/blob/9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e/sandbox/linux/services/namespace_sandbox.cc)
- [LaunchProcess / ForkWithFlags](https://github.com/chromium/chromium/blob/9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e/base/process/launch_posix.cc)
- [Namespace feature detection](https://github.com/chromium/chromium/blob/9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e/sandbox/linux/services/namespace_utils.cc)

## Preserved restrictions and limitations

The exact baseline prefix is retained: clone3 returns ENOSYS without
CAP_SYS_ADMIN; io_uring remains denied; the canonical socket argument-40
restriction is preserved; setns, mount, pivot_root and unrelated namespace creation remain denied under the
intended empty-capability profile. Newer baseline allowances such as Landlock,
openat2 and close_range are retained. This is **not** the older Playwright JSON.

This is not proof of complete AF_VSOCK containment. The inherited baseline permits
`socketcall`, which is relevant to the retained x86 compatibility ABI. Its
full-word `socket` argument comparison also permits `0x100000028` in the static
model; the kernel may then truncate an `int` argument to 40. These inherited
compatibility/argument-width gaps are unchanged by this proposal. The tests
record them instead of silently hardening the baseline or claiming them away.
Actual compiled-filter and transport containment remain unproven activation-review
obligations. See [seccomp argument truncation](https://man7.org/linux/man-pages/man2/seccomp.2.html)
and [socketcall(2)](https://man7.org/linux/man-pages/man2/socketcall.2.html).

The profile does not provide capabilities or override AppArmor. Docker's
no-new-privileges, cap-drop=ALL, UID 1000, network=none, read-only root, no host
mounts/devices/ports, private namespaces, bounded tmpfs, CPU/memory/PID limits and
Chromium sandbox remain mandatory and unchanged. However, a seccomp JSON file
cannot enforce those Docker settings. Any future selector must independently
validate them and reject capability additions or unsupported versions.

Allowing user-namespace creation necessarily exposes additional kernel code and
permits namespace-scoped capabilities in newly created child namespaces; it does
not give capabilities in the parent/host user namespace. NNP prevents privilege
gains through exec, but does not prohibit gaining capabilities when creating a
new user namespace. This is a real security-policy expansion, even though its
purpose is enabling Chromium's inner sandbox. A compromised process can use
these exact allowances too; seccomp does not bind them to Chromium call sites.

`chroot` still requires CAP_SYS_CHROOT **in the caller's user namespace**. The
initial worker lacks that capability, but Chromium can obtain it within its own
new user namespace. Classic seccomp cannot dereference the path pointer and
cannot constrain the allowed path to Chromium's fdinfo path, so the proposed
rule allows any kernel-authorized chroot. chroot alone is not a secure jail;
open descriptors, cwd and parent namespaces require separate containment. The
unchanged outer mount/network/cgroup boundaries remain essential, and kernel
vulnerabilities remain a residual risk. See [chroot(2)](https://man7.org/linux/man-pages/man2/chroot.2.html),
[user_namespaces(7)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)
and [NNP](https://www.kernel.org/doc/html/latest/userspace-api/no_new_privs.html).

AppArmor may still prevent namespace operations. Its restriction flag alone does
not prove a particular denial, and this proposal neither changes nor bypasses
AppArmor. It may also fail on runtime/browser differences or other syscalls.
Unexpected failures must stop the gate, not trigger broader fallback permissions.

## Required before any activation

1. Independent security review of this exact hash/delta, including compatibility
   ABIs, socketcall/argument-width containment gaps, child-namespace/chroot
   consequences and current engine/kernel provenance.
2. Explicit per-action approval for selecting this container-scoped policy.
   This preparation approval does not authorize activation or experiments.
3. Separately reviewed selector/inspection and policy-bound receipt changes;
   Docker-default or old receipts must not certify a changed profile.
4. After approval only, fresh positive browser and adversarial network,
   filesystem, namespace, resource and cleanup proofs under the exact profile.
   Static tests here do not simulate the kernel, AppArmor or libseccomp compiler.
5. Stop for a separate decision if additional permissions are needed. Never
   weaken host settings, add capabilities, disable sandboxing, use unconfined
   policies, or substitute host-browser success for isolated acceptance.
