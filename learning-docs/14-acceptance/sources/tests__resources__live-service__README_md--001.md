# tests/resources/live-service/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/resources/live-service/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L23。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1301`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/resources/live-service/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "db2bf28224398c9e395a3bc3e5b1d9ca60506cd85706c30c089a7d2bc9cf3e14"} -->
````markdown
<!-- tests/resources/live-service/README.md -->
# Explicitly authorized public test CA

The user authorized committing `caddy-root.pem` on 2026-10-11 for the test client
of `https://170.106.181.109:8317/v1` only. It contains one public CERTIFICATE,
no private key. Source: reviewed Git blob `5f74599575e83c730b7f30dc1482bf343ad1c19f`.

SHA256 certificate fingerprint:
`15:DB:86:A8:D1:15:66:62:5D:42:20:51:59:91:72:7C:90:0E:23:2E:64:1D:8E:7F:CB:08:B0:B4:2D:30:79:AF`.

Subject: `CN=Caddy Local Authority - 2026 ECC Root`. Self-signature verified.
Validity: 2026-10-11 02:59:32 UTC through 2036-08-19 02:59:32 UTC.
This root does not prove the live leaf certificate has the correct IP SAN.

Only `scripts/live_test_client.py` loads it into a scoped SSLContext after checking
the fingerprint and exact endpoint. Host/IP verification and certificate-chain
validation remain enabled. The transport allows only this service's model probe
and Chat Completions paths. It never installs a system root, changes proxy
settings, follows redirects, or disables TLS verification.

The user's no-charge declaration is recorded separately from TLS trust. Paid
mode still requires a positive explicit ceiling and conservative tariff; free
mode requires explicit acknowledgement and exact endpoint binding. Request,
step, token and duration limits continue to apply.
````
