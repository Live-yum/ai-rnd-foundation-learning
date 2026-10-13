# tests/resources/live-service/caddy-root.pem · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/resources/live-service/caddy-root.pem`；**本文件共有 1 段**。本段覆盖源文件 L1–L11。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`631`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/resources/live-service/caddy-root.pem", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "48a04702c6c1bb666a5b7d514ea11327735e25d311a579e97f2c150e01cae8d0"} -->
````text
# tests/resources/live-service/caddy-root.pem
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQPe3zHvHA/DOlIIDwdYp6YjAKBggqhkjOPQQDAjAwMS4w
LAYDVQQDEyVDYWRkeSBMb2NhbCBBdXRob3JpdHkgLSAyMDI2IEVDQyBSb290MB4X
DTI2MTAxMTAyNTkzMloXDTM2MDgxOTAyNTkzMlowMDEuMCwGA1UEAxMlQ2FkZHkg
TG9jYWwgQXV0aG9yaXR5IC0gMjAyNiBFQ0MgUm9vdDBZMBMGByqGSM49AgEGCCqG
SM49AwEHA0IABC6KL/iK7WLjkHOtOH7mIN3husi6BoOPNzl5ogyPVQS65kjE3jW0
bl+EcRV5waBK8Gqzqha1qPv08Ci5mxshV4yjRTBDMA4GA1UdDwEB/wQEAwIBBjAS
BgNVHRMBAf8ECDAGAQH/AgEBMB0GA1UdDgQWBBTMogrnvdAuMgKAawFyPXdBf8wL
HjAKBggqhkjOPQQDAgNJADBGAiEA6zaLgRQ7VrvXVfLo1UnMSGp5vYVsGl4wfOhl
ipjD1tQCIQCFRpGgMI/aOUR63zaIq/qFmCKZ2hkJRGNKXocw0/0HQg==
-----END CERTIFICATE-----
````
