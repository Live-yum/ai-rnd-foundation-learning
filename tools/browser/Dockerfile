# Build-time network is only for pinned official tooling; runtime has no network.
FROM mcr.microsoft.com/playwright:v1.56.1-noble AS probe-build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
COPY scripts/capability_browser_seccomp_probe.c /tmp/probe.c
RUN gcc -std=c11 -O2 -Wall -Wextra -Werror -static -fno-pie -no-pie /tmp/probe.c -o /opt/browser-seccomp-probe

FROM mcr.microsoft.com/playwright:v1.56.1-noble
WORKDIR /opt/verifier
COPY --from=probe-build /opt/browser-seccomp-probe /opt/browser-seccomp-probe
RUN npm install --ignore-scripts --no-audit --no-fund --package-lock=false playwright@1.56.1
COPY scripts/capability_browser.cjs scripts/capability_browser_worker.cjs scripts/capability_browser_network_probe.cjs ./
COPY scripts/capability_browser_apparmor.cjs scripts/capability_browser_seccomp_probe.c ./
COPY tools/browser/review-only-v2/chromium141-docker28-native-amd64.proposal.json ./browser-seccomp-v2.json
COPY tools/browser/Dockerfile ./Dockerfile
COPY tools/browser/seccomp.playwright-1.56.1.json tools/browser/LICENSE.playwright ./
RUN chmod -R a-w /opt/verifier && mkdir /opt/readonly-probe && chown 1000:1000 /opt/readonly-probe && chmod 700 /opt/readonly-probe
USER 1000:1000
ENV HOME=/tmp TMPDIR=/tmp
ENTRYPOINT ["node", "/opt/verifier/capability_browser_worker.cjs"]
