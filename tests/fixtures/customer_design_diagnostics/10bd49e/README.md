# Actual approved Plan, later rejected by customer acceptance

`python-approved-plan.json` is the exact normalized synthetic customer Plan from
DeepSeek run [36803597792](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36803597792),
job `110183065253`, source commit `10bd49e7e77e94dc8d2670fc949ef4ec9dad1876`, artifact `11136602792`.
SHA-256: `f4638440b66622db35ffd919613aa608656889eb5a1d96ee80651fbf7e0c19f0`.
The workflow reached READY but separate customer acceptance rejected the extra
`customers.published_on` field. This fixture is used only to replay that validation
failure, never as a substitute for a genuine model generation or delivery result.
