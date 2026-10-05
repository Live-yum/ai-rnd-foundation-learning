# Independent contest extension oracle, v2

## Evidence boundary

This is an **authored reference acceptance contract**, not an approved complete design,
not model-generated implementation evidence, and not proof of the full competition
website. It exercises a bounded native FastapiAdmin/PostgreSQL slice. The implementation
fixture is authored separately in `tests/fixtures/contest_native`; the oracle never
imports it. Unit tests use deliberately faulty simulated candidates; their passing
means the oracle rejects those faults, not that the native product passed.

`tests/fixtures/contest_oracle/original_requirement.json` preserves all 35 canonical
source units from the exact supplied requirement text. `source-0-N` IDs come from the
existing `scope_sources` algorithm applied to that synthetic replay's one message.
They are not IDs taken from a historical production run. Each atomic goal ID binds
contract version, source ID, exact original text and semantic assertion with SHA-256.
Every complete original source remains an explicit open obligation; passing capacity,
code joining, blind projection and outsider denial does not close the larger compound
requirements. In particular, cross-school rules, contribution ordering, teacher review,
random expert allocation, weighted scores, notifications, storage, exports, full UI and
end-to-end registration workflow remain unimplemented/unverified.

## Trusted placement and integration

The verifier controller must load `scripts/extension_oracles/contest.py` and the frozen
reference JSON from its trusted bundle, **outside the editable candidate tree**. Do
not mount them writable or readable to candidate processes. A source checkout being
writable by a developer is not a runtime immutability boundary. Hash the reviewed
bundle at construction and include hashes in the root-owned acceptance record. Never
accept hashes, goal bindings, SQL, assertions or success records from the candidate.

The controller provides:

- `http(actor, method, path, payload) -> (status, normalized_json_dict)`: bounded HTTP;
  native credentials/tokens for distinct synthetic captain, member_a, member_b,
  outsider, reviewer. `anonymous` has no credentials. Unwrap native success envelopes
  in this trusted adapter. Concurrent calls use independent connections.
- `database_probe(sql, params) -> list[dict]`: fixed SQL executed through the
  independently authenticated, read-only `rnd_verify` PostgreSQL account. Its private
  credential is read only by the trusted controller wrapper; application code cannot
  access it. The actual database session never authenticates as postgres or uses
  SET ROLE from a privileged session. This is never an application endpoint and
  cannot be faked with a candidate-provided JSON snapshot. Relation/catalog checks and
  reads share one locked read-only transaction, with row security disabled to fail
  closed, index scans disabled, statement/lock timeouts, and 64 KiB output file limits. SQL constants are fixed in
  the oracle. The app has only its isolated database role, no verifier credentials.
- Supervisor-generated process generation identifiers. `after_restart` requires a
  changed generation and unchanged real database identity. Do not accept app-reported
  PIDs or an arbitrary claim that restart occurred.

Call `initial`, stop the owned app process group, start a new group against the same
PG database, then call `after_restart`. Create a distinct isolated database and invoke
`fresh_database`, then replay `initial` there. Collect witnesses only from successful
trusted calls. Partial/failed calls never grant a complete verdict. Never edit global
or user databases. This oracle uses synthetic names and random per-execution markers;
no mail/SMS/cloud uploads, real student data or paid model calls occur.

## Fixed bounded HTTP and storage contract

All paths start with `/rnd/contest`; native framework authentication remains in use.

- `POST /teams`: captain posts `name`, `capacity`, `submission_title`; 200/201 with `id`.
- `POST /teams/{id}/invitations`: captain posts `expires_in_seconds`; 200/201 with `id`
  and opaque URL-safe `code`, at least 32 characters. Invitations are bearer codes,
  not user-bound approval. The code alone never removes the requirement to log in.
- `POST /invitations/redeem`: authenticated student posts `code`. New membership
  returns 200/201; full team 409; invalid code 404; expired/revoked code 410. Replaying
  a successful still-active code as an existing member returns 200 without duplicate
  membership. Captain already consumes one slot.
- `POST /invitations/{id}/revoke`: captain 200; outsider 403/404.
- `GET /teams/{id}`: captain gets `id`, `name`, `member_ids`; outsider and reviewer are
  denied. Nonmembers do not gain team reads from guessed IDs.
- `GET /review/teams/{id}`: reviewer receives exactly `id` and `submission_title`;
  nonreviewers are denied. Strict response equality forbids identity aliases, nested
  metadata or accidentally exposed relations. This is not proof that submitted
  documents themselves contain no personally identifying content.

The oracle issues an active 300-second code, a 1-second code and a revoked 300-second
code. Short TTL is an authored test parameter, not a user-specified production policy.
It waits 1.2 seconds before testing expiry. Two authenticated members then redeem the
same active code concurrently for one remaining slot: exactly one succeeds. An
invalid opaque code, unauthorized code issuance/revocation, anonymous redemption,
nonreviewer blind-view access and outsider reads are all denied. Possession of a valid
code permits a logged-in student to join; “outsider denial” does not contradict that.
No general brute-force/rate-limit guarantee is claimed by this version. A production
rate-limit policy and tests remain a separate obligation.

Physical tables are `rnd_contest_team`, `rnd_contest_membership`,
`rnd_contest_invitation`. The independent probe compares submitted random values,
exact membership cardinality, hashes of issued codes and revoked state. API-only or
in-memory implementations fail. Restart must retain all checked values and fresh DB
replay must not inherit old records.

## What passing means

`initial` returns five named semantic witnesses; `after_restart` and `fresh_database`
return their own witnesses. `coverage` accepts exact predicate names, never attached
lists of goal IDs or a health result. A health-only candidate, overfill, duplicated
membership, bypassed code ownership management, ignored expiry/revocation, unknown
code acceptance, identity leakage, role bypass and missing/wrong physical rows are
all covered by adversarial unit simulations.

The full original request always remains incomplete in this v2 slice. A future
real-model run must independently produce its candidate from the original prompt
and pass these trusted gates; an authored fixture must never be relabeled as that run.
