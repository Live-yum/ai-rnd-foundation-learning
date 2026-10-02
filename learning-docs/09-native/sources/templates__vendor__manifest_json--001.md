# templates/vendor/manifest.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：第三方源码来源与许可证。** 模板属于第三方依赖。manifest记录固定提交、归档哈希、逐文件内容摘要及排除项；LICENSE原样保留。只从教材也可以用vendor_templates --fetch重建源码归档，不需要复制本仓库已有ZIP。

**对应关系：** scripts/vendor_templates.py → manifest/ZIP → workbench/vendor.py → 原生生成器。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/vendor/manifest.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L105。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3890`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/vendor/manifest.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c8e046a735dc366d47fb3febaf7ee20ec5da5f19afe4b4ec2796247e327820e3"} -->
````json
// templates/vendor/manifest.json
{
  "format": 1,
  "storage": "ordinary-git-source-archives",
  "sources": [
    {
      "name": "fastapiadmin",
      "template": "fastapiadmin",
      "slot": "fastapiadmin",
      "url": "https://github.com/fastapiadmin/FastapiAdmin.git",
      "sha": "1cd12c726ad9032c17ef85ce805ce991be60fbdf",
      "archive": "fastapiadmin.zip",
      "license": "MIT",
      "archive_sha256": "015ad88bbfaf2d8a6c861d381150d7c4c77d98a4d3c4874e409126fc943bc505",
      "source_digest": "fa61c90dbbb8751d4e2261bce7000e6198bf2535b0dd102ba2426baa1355b2bc",
      "files": 1136,
      "excluded_files": [
        "frontend/app/.env.development",
        "frontend/app/.env.production",
        "frontend/web/.env"
      ]
    },
    {
      "name": "yudao-backend",
      "template": "yudao-vben",
      "slot": "backend",
      "url": "https://github.com/yudaocode/yudao-cloud-mini.git",
      "sha": "47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be",
      "archive": "yudao-backend.zip",
      "license": "MIT",
      "archive_sha256": "c13c12134f60d2cb592064aad7157bd7a05326b662830a896bc029cd15defc1d",
      "source_digest": "cca9e2f812e34a2be0da5f7d065cfa604d0a287faeb2c40af7f00068f18a30d4",
      "files": 1408,
      "excluded_files": []
    },
    {
      "name": "yudao-frontend",
      "template": "yudao-vben",
      "slot": "frontend",
      "url": "https://github.com/yudaocode/yudao-ui-admin-vben.git",
      "sha": "1b14e889f529e245fd620daa720dcea6de0cc5e7",
      "archive": "yudao-frontend.zip",
      "license": "MIT",
      "archive_sha256": "d8aaf8baa5f9a9fccda35d427fba42b167dab96f2dc9096f129c055c69c4e7b1",
      "source_digest": "cf0951f33e174130be6815b8bd0008ea4f45e1ae3625be240f9698f2c08b6568",
      "files": 12112,
      "excluded_files": [
        "apps/web-antd/.env",
        "apps/web-antd/.env.analyze",
        "apps/web-antd/.env.development",
        "apps/web-antd/.env.production",
        "apps/web-antd/src/views/bpm/components/simple-process-design/styles/iconfont.ttf",
        "apps/web-antd/src/views/bpm/components/simple-process-design/styles/iconfont.woff",
        "apps/web-antd/src/views/bpm/components/simple-process-design/styles/iconfont.woff2",
        "apps/web-antdv-next/.env",
        "apps/web-antdv-next/.env.analyze",
        "apps/web-antdv-next/.env.development",
        "apps/web-antdv-next/.env.production",
        "apps/web-antdv-next/src/views/bpm/components/simple-process-design/styles/iconfont.ttf",
        "apps/web-antdv-next/src/views/bpm/components/simple-process-design/styles/iconfont.woff",
        "apps/web-antdv-next/src/views/bpm/components/simple-process-design/styles/iconfont.woff2",
        "apps/web-ele/.env",
        "apps/web-ele/.env.analyze",
        "apps/web-ele/.env.development",
        "apps/web-ele/.env.production",
        "apps/web-ele/src/views/bpm/components/simple-process-design/styles/iconfont.ttf",
        "apps/web-ele/src/views/bpm/components/simple-process-design/styles/iconfont.woff",
        "apps/web-ele/src/views/bpm/components/simple-process-design/styles/iconfont.woff2",
        "apps/web-naive/.env",
        "apps/web-naive/.env.analyze",
        "apps/web-naive/.env.development",
        "apps/web-naive/.env.production",
        "apps/web-tdesign/.env",
        "apps/web-tdesign/.env.analyze",
        "apps/web-tdesign/.env.development",
        "apps/web-tdesign/.env.production"
      ]
    }
  ],
  "exclusions": [
    ".data",
    ".db",
    ".db-shm",
    ".db-wal",
    ".eot",
    ".git",
    ".key",
    ".otf",
    ".p12",
    ".pem",
    ".pfx",
    ".pytest_cache",
    ".ruff_cache",
    ".ttc",
    ".ttf",
    ".venv",
    ".woff",
    ".woff2",
    "__pycache__",
    "dist",
    "logs",
    "node_modules",
    "target"
  ],
  "note": "Source code, schemas and dependency locks are included. Build caches, runtime secrets and font binaries are not redistributed."
}
````
