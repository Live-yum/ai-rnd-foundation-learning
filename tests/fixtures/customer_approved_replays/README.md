# Approved synthetic customer replay

`yudao-1d7.json` is the byte-identical normalized Plan that passed design approval, native generation/verification, and independent model review in real DeepSeek run [36795375784](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36795375784), job 110157491211, source `1d7c70b03e63509830e97af9af398c0bd148902e`. The overall run then failed at ZIP extraction because the generic 10,000-entry ceiling rejected the full original Yudao monorepo. This fixture is not evidence that the downloaded product passed.

Artifact 11133539312 retained only this approved synthetic Plan after schema, size, known-key and credential-pattern rejection. Its SHA-256 is `16731f7c60a15916058d64c503525aafe93e1c53e0da62bae1eb8d0c227730f5` (19,534 bytes). The loader rechecks hash, template, schema, size and credential patterns before any replay.

The `approved-1d7` customer-runtime case regenerates this exact Plan with the original pinned native generator, consumes the distributable ZIP, and verifies an independent database, browser and restart. It makes no model calls. The genuine real-model workflow continues to obtain a fresh recommendation, Plan and independent review and never reads this fixture. Unapproved diagnostic artifacts in the sibling directory must never be used for generation.
