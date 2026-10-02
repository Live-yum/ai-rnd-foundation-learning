# tools/embeddings/pyproject.toml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：真实本机向量模型的独立验证环境。** 单独锁定向量模型运行依赖，避免大体积机器学习依赖混入平台与Aider环境。安装和公开模型权重下载是准备阶段，向量推理必须留在本机；不能用协议模拟响应冒充模型实际运行。

**对应关系：** 对应本机向量验收脚本 → 独立依赖环境与本地权重 → retrieval向量检索证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/embeddings/pyproject.toml`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`228`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/embeddings/pyproject.toml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1d7eb8eec5e2e149a5328543fadabb3618339e6659f6fb0c0ea29248fc19f9bf"} -->
````toml
# tools/embeddings/pyproject.toml
[project]
name = "rnd-local-embedding-runtime"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = ["onnxruntime==1.23.2", "tokenizers==0.22.1", "numpy==2.3.4", "huggingface-hub==0.36.0"]
[tool.uv]
package = false
````
