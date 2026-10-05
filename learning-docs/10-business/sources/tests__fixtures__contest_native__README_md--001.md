# tests/fixtures/contest_native/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/contest_native/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L49。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3208`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/contest_native/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ef98d1f89742cd580d04969f662d6ce6be11a6edc5069672253b3498a59181a0"} -->
````markdown
<!-- tests/fixtures/contest_native/README.md -->
# Human-authored native contest reference fixture

This fixture is deliberately human-authored CI input. It is not AI-generated
application evidence, a production implementation, or completion of the full
competition requirements. It mounts into the pinned FastapiAdmin backend and
uses its real application factory, session authentication and database dependency.

The bounded vertical covers atomic team membership capacity, opaque invitation-code redemption
idempotence, expiry/revocation, server-side authorization and a blind-review response allowlist.
Independent external oracles own the expected outcomes and inspect the PostgreSQL
state; they must not import this fixture's policy to compute the expected answer.

The source fixture remains outside the candidate workspace. A profile copies only
this module into the candidate's permitted plugin path. Native authentication,
framework source, CI orchestration and oracle code remain protected. Mutation
cases modify candidate copies, never this baseline or the oracle expectations.

Still open: student identity verification, cross-school policy configuration,
member contribution/order editing, large material uploads, teacher binding and
sign-off, administrative final approval, expert random assignment, configurable
weighted scoring, result publication, anti-cheating analysis, dashboards and
Excel/PDF exports. Passing this fixture proves only its declared subset.

Native mount destination: `backend/app/plugin/module_rnd/contest/`. The native
registry contributes `/rnd`; `ContestRouter` contributes `/contest`. Required
synthetic native role codes are `rnd_contest_student` and
`rnd_contest_reviewer`, provisioned by the trusted harness through native APIs.
There is no superuser shortcut in fixture authorization. Blind review currently
means a role-authorized, explicit response-field allowlist. Per-expert assignment
and redaction of identity that a student embeds inside their own submission title
remain separate, unverified requirements.

Contract version: `contest-business-v2`. Captains issue independent opaque
codes, with a 1–604800 second lifetime supplied by this synthetic fixture's
trusted test request. Tokens use 256 random bits; business rows store only their
SHA-256 digest. Redeeming an active code joins the referenced team. The same
member can repeat redemption without consuming another slot; another team's
member cannot switch teams through redemption. Concurrent acceptors serialize
on the physical team row. Native user, team and invitation locks have a fixed
order. Captains can revoke codes; unknown codes return 404 and expired/revoked
codes return 410. Fixture models enforce unique user membership and unique
code digests. This single-contest test does not implement cross-school rules.

This fixture does not add its own per-actor invalid-code rate limiting and does
not claim that protection is verified. The authenticated native session and the
existing native middleware remain in use. Code values are returned only when
issuing a code; the blind-review response exposes only id and submission_title.
The trusted harness owns test-token handling and must redact request bodies from
any exported reports.
````
