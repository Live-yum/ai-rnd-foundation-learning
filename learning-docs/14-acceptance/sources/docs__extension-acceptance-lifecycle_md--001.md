# docs/extension-acceptance-lifecycle.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本教材正文的源文件。** 上文正文就是这些源文件拼接后的内容。它们也收录在附录中，使从教材还原出的项目能再次生成逐字一致的完整教材，而不是只有一次性的代码快照。

**对应关系：** scripts/build_handbook.py的GUIDES → 正文 → 完整源码附录。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/extension-acceptance-lifecycle.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L163。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10292`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/extension-acceptance-lifecycle.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8051dbd76d4d6e06d62b19c875b1c3909327a554f8a675634218cecf22cb5177"} -->
````markdown
<!-- docs/extension-acceptance-lifecycle.md -->
# Source-bound extension acceptance and partial delivery

## What this increment proves

The generic execution minimum is still useful: positive/negative HTTP cases,
roles, a real browser, physical database writes and process restart. It does not
prove that a login/profile CRUD contract implements inventory overselling,
appointment rescheduling, or every clause in a compound original request.
Attaching those source IDs to the CRUD scenarios cannot mark them complete.

Every exact source unit now retains an `original.full_source` obligation. Unknown
coverage is explicitly incomplete, never a null value that passes a delivery gate.
The existing independently authored contest oracle still closes only its bounded
predicates. Its capacity/concurrent redemption, role, blind projection, exact
PostgreSQL rows, restart and fresh-database tests remain separate evidence.

## Explicit atomic review and execution

For the supported Python/SQLite profile, a plan may propose `obligations`:

- An immutable source ID and its existing source-unit digest
- One precise business assertion and the corresponding scenario
- A physical table, parameterized key, and expected column values
- A controller-generated nonce written through HTTP and read again after restart

The controller checks source hashes and IDs, referenced scenarios/tables, nonce
binding, and restart/real-runtime requirements before coding. The original source,
proposed decomposition, scenario and physical assertion are displayed together at
the design gate. This gate always requires an explicit local-operator approval;
intelligent mode and model review cannot approve it. The approval is read from the
durable store and bound to the exact run, stage, version and content digest.

`complete_source_ids` is a proposed exhaustive-decomposition statement for human
review, not a model verdict. The reviewer is responsible for the semantic
relevance and exhaustiveness of that decomposition. Runtime evidence proves the
frozen assertions, not arbitrary natural language. Result metadata preserves
`natural_language_semantics_proven: false` even when the reviewed contract closes.

The independent controller uses the trusted system interpreter to observe the actual
SQLite file through a bounded controller-private snapshot. It accepts no candidate
SQL, Python, supplied database snapshot or success report. Identifiers are constrained,
values are bound parameters, tables
must be physical, and the query must return exactly the expected row. Initial and
restart witnesses bind the same contract and values. A constant API response plus
an unrelated table write cannot satisfy this physical assertion. PostgreSQL
declarative obligations remain unsupported until a separate safe probe profile
exists; the registered contest oracle already provides fixed PostgreSQL probes.

The controller nonce cannot be overwritten by response captures. Physical columns
must really exist and cannot be generated/hidden columns; SQLite's double-quoted
string fallback cannot fake missing columns. Initial writers are drained. On restart,
the same application processes are paused using pinned process descriptors before
any replay request, then resumed only after the physical observation. Task identities
and scheduling counters detect resume/write/re-stop races. Expected values never
travel through process arguments or environment variables: the controller uploads a
bounded request into its root-private directory, validates owner/permissions/links,
and removes it after observation. This prevents a restarted candidate from reading
the challenge through process listings before the pause. No-follow directory/file
descriptors pin the source files and only their bounded private copies reach SQLite.
Committed WAL and empty/no rollback journal are supported; any nonempty rollback
journal fails closed before SQLite opens it, with no recovery or writable fallback.
Restart receipts bind both values and the exact
interpolated key, so selecting another same-valued row is not retention evidence.
SQLite Boolean storage assertions use explicit `0`/`1`, rather than claiming the
database reader returned JSON Booleans.

The real authored SQLite profile/security CI fixture now includes the consumer
launcher and an atomic obligation, so its successful receipt requires this actual
pre-replay path. Unit/supervisor tests alone are not relabeled as live Daytona proof.

## Honest partial delivery

If any original source remains open, the successful executable contract may still
be useful. After aggregate verification, a separate scope gate presents all open
source obligations and external prerequisites. Only explicit operator approval
allows the partial package; automatic continuation cannot consume that gate.
Approval is scoped to downloading that exact partial result, not to deleting or
closing any unmet requirement.

Reviewer-reported gaps are included in the exact scope approval, ZIP declaration
and final result. Because free-text findings do not reliably identify one source,
any unresolved finding conservatively reopens source-completeness claims while
preserving already passed atomic observations. The previous completion list remains
visible. Changed findings invalidate old scope approvals; a partial result cannot
silently hide a conflict about a previously closed source.

Once execution/model review is complete, scope and final delivery approval remain
available without a model configuration. The API and worker consult the exact
persisted gate and restrict model-free work to those delivery stages; stale,
cross-run or missing checkpoints cannot restart planning or coding. Exact approval
replays remain idempotent.
Transient packaging failures after an approved scope can also retry without a
model. Retry carries the persisted approval and original checkpoint job identity;
the worker permits only the saved packaging/delivery tail. A planning/coding or
missing checkpoint fails closed instead of spending a model call. The UI exposes
this retry only when the server marks that exact retained run eligible.

The ZIP contains `RND-DELIVERY.json`, including the original source units, coverage,
remaining obligations, dependency/migration/service readiness, and the explicit
partial label. Partial results use `SOURCE_READY` and
`full_request_complete: false`. A model review, forged approval dictionary, old
version, stale source inventory or changed execution evidence cannot authorize it.

## Real consumer entrypoint

New Python extension baselines contain controller-owned `RND-CONSUMER.json`.
It freezes a supported ASGI entrypoint, SQLite path, port and runtime identity.
The business coder cannot modify that contract or `start.py`.

The sandbox and extracted final ZIP now both start the actual packaged `start.py`
with the admitted preinstalled interpreter and unchanged existing isolation.
`PRODUCT_DATABASE_URL` and `DATABASE_URL` identify the same database. An ambient
platform `DATABASE_URL` is never adopted by the consumer launcher. The final
cleanroom receipt must prove the exact extracted source/plan, real cold startup,
business assertions, physical storage and data-preserving restart.

The custom application owns its initial schema bootstrap. Its schema must not be
silently mixed with the unrelated baseline Alembic schema. Cold bootstrap and a
same-schema restart are **not** evidence of migrating an old custom schema.
`existing_schema_migration` stays `unverified`; `--init-only` refuses to pretend
otherwise. A separate real standard-template test does exercise Alembic upgrade
with existing data, and is explicitly not a custom/native migration attestation.
Historical candidates retain their old bytes and need a new approved baseline for
consumer certification. FastapiAdmin consumer evidence remains explicitly absent
in this increment; its isolated runtime proof is not relabeled as ZIP startup.

## Readiness and resume boundaries

`extension-readiness.json` records exact plan/source/image identities, matched
readonly dependency evidence, requested dependency reviews, migration limitations
and external prerequisites. Retry retains the same candidate. A matching, already
qualified profile can satisfy the installed-dependency item; a changed source or
profile cannot borrow an old receipt. New packages still require separately
reviewed versions, licenses, locks and immutable image qualification.

External fixture tests verify adapters only. There is no supported live HTTP/S3
probe execution/authorization chain yet, so service and credential prerequisites
remain `awaiting-approved-independent-probe`. Manual acknowledgement, JSON upload,
model output or a fake successful provider receipt never changes that to verified.
This increment creates no credentials, access grants, outbound service calls,
production deployment, paid model calls or security-policy exceptions.

## Open-source integration choices

Reuse the existing pytest, Pydantic, SQLAlchemy/Alembic, isolated Node Playwright
and LangGraph/checkpointer dependencies. They already fit the controller boundary.
The changes add no dependency or orchestration framework.

Possible separately reviewed additions are pytest-alembic for migration histories
and seeded old-data tests, then Schemathesis/Hypothesis for adversarial API and
stateful checks. OpenAPI conformance cannot certify missing business requirements;
candidate applications must not be imported through an in-process ASGI test loader.
Native transitive wheels, exact versions/hashes, licenses and offline profile
admission need review before integration. StrictDoc can export traceability later,
but a report is not acceptance authority. Adding Temporal would add operational
surface without supplying semantic correctness or process isolation.

Primary upstream references:
- [Alembic autogenerate limitations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [pytest-alembic seeded data](https://pytest-alembic.readthedocs.io/en/latest/custom_data.html)
- [Schemathesis pytest checks](https://schemathesis.readthedocs.io/en/stable/tutorials/pytest/)
- [Hypothesis stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html)
- [LangGraph interrupt replay](https://docs.langchain.com/oss/python/langgraph/interrupts)
````
