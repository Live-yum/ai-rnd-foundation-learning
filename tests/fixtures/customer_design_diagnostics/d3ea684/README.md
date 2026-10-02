# Recorded d3ea684 diagnostics

These are sanitized synthetic customer-service CI artifacts from run 36899875461,
commit d3ea6848360054bc83792bb5c6defbe34409b0a9. They contain no provider credentials
or real customer records. The summaries preserve failed outcomes and source
provenance. The paired design files are explicitly unapproved, pure-validator
inputs: never approve, generate, execute, or replace them with corrected output.

- Fastapi: mixed keyword-search and exact-filter prose was bound across separate
  field lists although the explicit typed properties matched the candidate
- Yudao: a multi-role acceptance sentence invented service request creation; the
  typed grant-only contract did not grant it, and independent review blocked
  delivery. Schema-valid JSON does not prove arbitrary prose is semantically
  consistent. The fix constrains the existing analysis prompt and Pydantic schema;
  it does not grant the action or weaken independent review

Exact byte sizes and SHA-256 values are pinned in the offline regression tests.
Corrected synthetic cases are built independently in the tests. Genuine success
must be established by a new authorized full workflow on the final source SHA.
