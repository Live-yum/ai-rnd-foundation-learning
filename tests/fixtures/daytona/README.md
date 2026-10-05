# Pinned Daytona API image-reference fixture

`docker-image.util.ts` is an unchanged upstream file, used to execute the actual
parser and serializer before and after the local build patch. It is not a
reimplementation or live-container proof.

- Upstream: https://github.com/daytonaio/daytona/blob/01c502bb1f1ff8f2885d0cd490e043736083dca8/apps/api/src/common/utils/docker-image.util.ts
- Release: v0.190.0
- Git blob: `b0b03b28ce08b2865db9d2dc291c1745cb6492cf`
- Copyright 2025 Daytona Platforms Inc.; AGPL-3.0, included in `LICENSE`.
- Local change: `tools/daytona/api-digest-reference.patch`, applied only after
  checking the exact source blob and patch bytes by `scripts.daytona_build`.

The regression executes this TypeScript directly with Node's type stripping.
API build tests also reject source/revision/patch drift before any image build.
