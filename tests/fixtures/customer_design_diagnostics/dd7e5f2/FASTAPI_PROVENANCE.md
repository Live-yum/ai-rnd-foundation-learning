# FastapiAdmin unapproved diagnostic replay only

These two files are byte-exact copies of normalized diagnostics from genuine
DeepSeek Actions run [36840557604](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36840557604),
attempt 1, source commit `dd7e5f2135fdfe8b84f36dd1de5ab6e090c6a45a`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| fastapi-unapproved-design.json | 49980 | 9c8cdc4576208ee3f3954d724a7789e2f635e50ae25b66f65d75e34d0e41b5f5 |
| fastapi-summary.json | 17671 | a7782be7e86a74cfae44ca9ccad835107ac4a7de2e7fff9ebcb4d747b6138e7a |

The design envelope remains explicitly **unapproved**, **non-executable**, and
for **offline contract validation only**. Only pure Requirement/Plan validators
may read it or validate deep-copied synthetic mutations. Never approve, generate
from, execute, supply this candidate as provider output, or use it as delivery
proof or as a substitute for a future model-generated Plan.

The unchanged requirement has two positive service/customers/all permission
declarations, one granting read and one granting read_metrics. The unchanged
candidate correctly consolidates them into the sole Plan row allowed for that
role/resource. The original summary records two false coverage gaps and two
schema-rejected repair attempts to duplicate permission rows. The regression
accepts their exact semantic action union within the same source collection;
independent matrices, restrictions, row scopes, extra actions, foreign grants,
and malformed declarations remain binding. A pure validator pass is not model
workflow completion, design approval, runtime acceptance, or delivery proof.
