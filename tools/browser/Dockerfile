# Build-time network is only for pinned official tooling; runtime has no network.
FROM mcr.microsoft.com/playwright:v1.56.1-noble
WORKDIR /opt/verifier
RUN npm install --ignore-scripts --no-audit --no-fund --package-lock=false playwright@1.56.1
COPY scripts/capability_browser.cjs scripts/capability_browser_worker.cjs scripts/capability_browser_network_probe.cjs ./
COPY tools/browser/Dockerfile ./Dockerfile
COPY tools/browser/seccomp.playwright-1.56.1.json tools/browser/LICENSE.playwright ./
RUN chmod -R a-w /opt/verifier && mkdir /opt/readonly-probe && chown 1000:1000 /opt/readonly-probe && chmod 700 /opt/readonly-probe
USER 1000:1000
ENV HOME=/tmp TMPDIR=/tmp
ENTRYPOINT ["node", "/opt/verifier/capability_browser_worker.cjs"]
