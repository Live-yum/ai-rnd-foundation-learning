# tools/browser/review-only-v2/proposal-manifest.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/browser/review-only-v2/proposal-manifest.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L35。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1610`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/browser/review-only-v2/proposal-manifest.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "14b57c1a21026efa35184b68522415a4b838e8aed9c9697816d1c253f2305f75"} -->
````json
// tools/browser/review-only-v2/proposal-manifest.json
{
  "status": "approved-actions-only-pending-live-proof",
  "activation_authorized": true,
  "live_validation": false,
  "baseline_path": "../review-only/moby-v28.0.4-default.json",
  "baseline_sha256": "9c1025c88ccaa517b648da571961838744ea2137f176bfe6a48b21294cae9c76",
  "baseline_provenance_manifest": "../review-only/proposal-manifest.json",
  "proposal_file": "chromium141-docker28-native-amd64.proposal.json",
  "proposal_sha256": "9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f",
  "supported_target": {
    "daemon_arch": "amd64",
    "image_arch": "amd64",
    "docker_version": "28.0.4",
    "initial_caps": [],
    "process_abi": "x86_64"
  },
  "allowed_syscall_abis": [
    "SCMP_ARCH_X86_64"
  ],
  "changes": [
    "native amd64 syscall ABI only; no x86/x32 compatibility ABI",
    "remove socketcall from unconditional allows",
    "replace socket and socketpair broad allowances with exact low32 != AF_VSOCK complement",
    "preserve the five exact Chromium namespace/chroot allowances from v1"
  ],
  "offline_validation": "libseccomp export plus bounded classic-BPF evaluation only; no filter loaded; not CI compiler or kernel proof",
  "required_before_activation": [
    "independent review",
    "explicit per-action approval",
    "wire and review fail-closed observed-target guard",
    "actual runtime/compiler/kernel/policy provenance and receipt binding",
    "fresh positive and adversarial network, filesystem, resource, namespace and cleanup evidence"
  ],
  "activation_scope": "Disposable offline Actions browser workers only; explicit fixed-hash selector"
}
````
