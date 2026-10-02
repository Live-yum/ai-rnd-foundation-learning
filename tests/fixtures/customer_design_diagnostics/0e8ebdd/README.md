# Unapproved diagnostic replay only

These are byte-exact, normalized diagnostics from genuine DeepSeek Actions run
[36826237130](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36826237130),
at source commit `0e8ebdd0c74a86538b648d55b9fe56dcc71a9de9`.
The `*-summary.json` files retain the original failure messages, source indices,
provider receipts, and run identity unchanged. The Python job was `110252442739`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| python-unapproved-design.json | 49293 | a492b0e6e379b6062698bfde77b05a52ba81aab7e7b47d2a84e15e5173fd7ab6 |
| python-summary.json | 18684 | b64b86827ef6ecd63df33ca9fdb3c08ac9b2b9917adc2f32a9e1f1871159f929 |
| yudao-unapproved-design.json | 48753 | dd7bf0dbe805ae9d1527b899bd014fd87e1c69179b2134748cdf7d49b0d7c115 |
| yudao-summary.json | 28816 | 755265754504037327c38c643592894c51cd9789ac399023f1037b6b299c5631 |

Both design envelopes are explicitly unapproved, non-executable, and for offline
contract validation only. Only pure Requirement/Plan validators may replay them
or validate deep-copied synthetic mutations. Never approve, generate from,
execute, supply these candidates as provider output, or use them as delivery
proof or substitutes for a future model-generated Plan.

The original Python diagnostics contain two false positives: a forbidden-field
mention interpreted as a required field, and a multi-metric list interpreted as
one filtered metric. The original Yudao diagnostics contain two false broad
search-target obligations plus seven genuine typed `searchable=False` conflicts.
Tests preserve those seven conflicts on the unchanged Yudao candidate; a separate
synthetic deep copy corrects only its explicit false flags. A pure validator pass
is not workflow completion, approval, or customer acceptance.
