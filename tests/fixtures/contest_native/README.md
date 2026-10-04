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
