# tools/browser/review-only/proposal-manifest.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/browser/review-only/proposal-manifest.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L176。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4505`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/browser/review-only/proposal-manifest.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8b82fca4f81ea0f2ad244ca9fe4d2c4a740cf88b74b71266836008db0cf7d36b"} -->
````json
// tools/browser/review-only/proposal-manifest.json
{
  "status": "inactive-review-only",
  "activation_authorized": false,
  "live_validation": false,
  "scope": {
    "engine": "28.0.4",
    "architecture": "amd64",
    "chromium": "141.0.7390.37",
    "playwright": "1.56.1",
    "initial_capability_bounding_set": []
  },
  "baseline": {
    "file": "moby-v28.0.4-default.json",
    "upstream_url": "https://github.com/moby/moby/blob/6430e49a55babd9b8f4d08e70ecb2b68900770fe/profiles/seccomp/default.json",
    "upstream_commit": "6430e49a55babd9b8f4d08e70ecb2b68900770fe",
    "sha256": "9c1025c88ccaa517b648da571961838744ea2137f176bfe6a48b21294cae9c76",
    "representation": "UTF-8 content returned by the GitHub connector, preserved without reformatting"
  },
  "proposal": {
    "file": "chromium141-docker28-amd64.proposal.json",
    "sha256": "f62d10d5ce466dfd0714d61891ef7b94445367c8a6a303302f4c3956687f3504"
  },
  "upstream_license": "LICENSE.moby",
  "chromium_sources": [
    {
      "url": "https://github.com/chromium/chromium/blob/9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e/sandbox/linux/services/namespace_sandbox.cc",
      "sha256": "ae3ecf1e474c970cfbe5413b1ec3aa99895f3dcced7c1ae774955c307218cd8c",
      "representation": "UTF-8 content returned by the GitHub connector"
    },
    {
      "url": "https://github.com/chromium/chromium/blob/9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e/sandbox/linux/services/credentials.cc",
      "sha256": "43e3968be3683c5c81b3992c97e113668d5bc83e06e0f0e3ca9236f4dedce372",
      "representation": "UTF-8 content returned by the GitHub connector"
    },
    {
      "url": "https://github.com/chromium/chromium/blob/9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e/base/process/launch_posix.cc",
      "sha256": "6b4c567d78c6ae4ec5899521c152ed4765041b9d29baf269370743c9efe264e0",
      "representation": "UTF-8 content returned by the GitHub connector"
    },
    {
      "url": "https://github.com/chromium/chromium/blob/9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e/sandbox/linux/services/namespace_utils.cc",
      "sha256": "ccc94e6dc8ec2d7f0eeb1e37362dbbd343ef23da952ecabe801f491d69cff1c0",
      "representation": "UTF-8 content returned by the GitHub connector"
    }
  ],
  "json_patch": [
    {
      "op": "add",
      "path": "/syscalls/-",
      "value": {
        "names": [
          "clone"
        ],
        "action": "SCMP_ACT_ALLOW",
        "includes": {
          "arches": [
            "amd64"
          ]
        },
        "excludes": {
          "caps": [
            "CAP_SYS_ADMIN"
          ]
        },
        "args": [
          {
            "index": 0,
            "value": 268435473,
            "op": "SCMP_CMP_EQ"
          }
        ]
      }
    },
    {
      "op": "add",
      "path": "/syscalls/-",
      "value": {
        "names": [
          "clone"
        ],
        "action": "SCMP_ACT_ALLOW",
        "includes": {
          "arches": [
            "amd64"
          ]
        },
        "excludes": {
          "caps": [
            "CAP_SYS_ADMIN"
          ]
        },
        "args": [
          {
            "index": 0,
            "value": 1879048209,
            "op": "SCMP_CMP_EQ"
          }
        ]
      }
    },
    {
      "op": "add",
      "path": "/syscalls/-",
      "value": {
        "names": [
          "clone"
        ],
        "action": "SCMP_ACT_ALLOW",
        "includes": {
          "arches": [
            "amd64"
          ]
        },
        "excludes": {
          "caps": [
            "CAP_SYS_ADMIN"
          ]
        },
        "args": [
          {
            "index": 0,
            "value": 536870929,
            "op": "SCMP_CMP_EQ"
          }
        ]
      }
    },
    {
      "op": "add",
      "path": "/syscalls/-",
      "value": {
        "names": [
          "unshare"
        ],
        "action": "SCMP_ACT_ALLOW",
        "includes": {
          "arches": [
            "amd64"
          ]
        },
        "excludes": {
          "caps": [
            "CAP_SYS_ADMIN"
          ]
        },
        "args": [
          {
            "index": 0,
            "value": 268435456,
            "op": "SCMP_CMP_EQ"
          }
        ]
      }
    },
    {
      "op": "add",
      "path": "/syscalls/-",
      "value": {
        "names": [
          "chroot"
        ],
        "action": "SCMP_ACT_ALLOW",
        "includes": {
          "arches": [
            "amd64"
          ]
        },
        "excludes": {
          "caps": [
            "CAP_SYS_ADMIN"
          ]
        }
      }
    }
  ]
}
````
