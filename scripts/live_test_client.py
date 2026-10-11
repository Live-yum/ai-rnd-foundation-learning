"""Explicit test-only trust for the user-owned service; never a system CA change."""

import argparse
import hashlib
import json
import os
import re
import ssl

import httpx

from workbench.filesystem import write_json
from workbench.model_diagnostics import transport_failure
from workbench.settings import ROOT

ENDPOINT = "https://170.106.181.109:8317/v1"
CA = ROOT / "tests/resources/live-service/caddy-root.pem"
FINGERPRINT = "15db86a8d11566625d4220515991727c900e232e641d8e7fcb08b0b42d3079af"
ATTESTATION = "user-confirmed-no-charge-2026-10-11"


def zero_billing(env):
    if env.get("LIVE_BILLING_MODE", "metered") != "declared_free":
        raise ValueError("explicit_zero_billing_mode_required")
    if (
        env.get("LIVE_ZERO_BILLING_ACK") != "true"
        or env.get("BASE_URL", "").rstrip("/") != ENDPOINT
    ):
        raise ValueError("zero_billing_confirmation_or_endpoint_missing")
    return {
        "mode": "declared_free",
        "attestation": ATTESTATION,
        "endpoint": ENDPOINT,
        "source": "user_declaration_not_provider_invoice",
        "maximum_cost_usd": 0,
    }


def test_context(endpoint, mode):
    if mode not in {"system", "caddy-ip"}:
        raise ValueError("unknown_test_ca_mode")
    context = ssl.create_default_context()
    if mode == "caddy-ip":
        if endpoint.rstrip("/") != ENDPOINT:
            raise ValueError("test_ca_endpoint_mismatch")
        pem = CA.read_text(encoding="ascii")
        if "PRIVATE KEY" in pem or not re.fullmatch(
            r"-----BEGIN CERTIFICATE-----\n[A-Za-z0-9+/=\r\n]+-----END CERTIFICATE-----\s*", pem
        ):
            raise ValueError("public_certificate_only")
        if hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest() != FINGERPRINT:
            raise ValueError("test_ca_fingerprint_mismatch")
        context.load_verify_locations(cadata=pem)
    if not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
        raise ValueError("strict_tls_required")
    return context


class TestServiceTransport(httpx.BaseTransport):
    """Restrict the scoped trust to two exact endpoints, with no redirects."""

    def __init__(self, endpoint, mode="system"):
        self.endpoint = endpoint.rstrip("/")
        self.inner = httpx.HTTPTransport(
            verify=test_context(self.endpoint, mode), retries=0, trust_env=False
        )
        self.calls = self.responses = 0

    def handle_request(self, request):
        allowed = (
            request.method == "GET"
            and str(request.url) == self.endpoint + "/models"
            and "authorization" not in request.headers
        ) or (request.method == "POST" and str(request.url) == self.endpoint + "/chat/completions")
        if not allowed:
            raise ValueError("test_transport_destination_rejected")
        if request.method == "POST":
            self.calls += 1
        response = self.inner.handle_request(request)
        if request.method == "POST":
            self.responses += 1
        return response

    def close(self):
        self.inner.close()


def probe(env):
    if (
        env.get("GITHUB_ACTIONS") != "true"
        or env.get("GITHUB_REPOSITORY") != "Live-yum/ai-rnd-foundation-learning"
        or env.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
        or env.get("GITHUB_RUN_ATTEMPT") != "1"
        or not re.fullmatch(r"[a-f0-9]{40}", env.get("GITHUB_SHA", ""))
        or env.get("REVIEWED_SHA") != env.get("GITHUB_SHA")
    ):
        raise ValueError("reviewed_first_manual_dispatch_required")
    endpoint = env.get("BASE_URL", "").rstrip("/")
    if not endpoint.startswith("https://"):
        raise ValueError("https_required")
    mode = env.get("LIVE_TEST_CA", "system")
    billing = (
        zero_billing(env)
        if mode == "caddy-ip" or env.get("LIVE_BILLING_MODE") == "declared_free"
        else {"mode": "metered"}
    )
    with httpx.Client(
        transport=TestServiceTransport(endpoint, mode),
        timeout=20,
        follow_redirects=False,
        trust_env=False,
    ) as client:
        with client.stream("GET", endpoint + "/models") as response:
            if response.status_code not in {200, 401}:
                raise ValueError("unauthenticated_service_probe_rejected")
            return {
                "strict_tls": True,
                "http_status": response.status_code,
                "authentication_sent": False,
                "head_sha": env["GITHUB_SHA"],
                "ca_mode": mode,
                "ca_sha256": FINGERPRINT if mode == "caddy-ip" else None,
                "billing": billing,
            }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    receipt = {"strict_tls": False, "authentication_sent": False}
    try:
        receipt = probe(os.environ)
    except Exception as exc:
        diagnostic = transport_failure(exc)
        receipt["failure"] = diagnostic[0] if diagnostic else "strict_unauthenticated_probe_failed"
        raise SystemExit(1) from None
    finally:
        write_json(ROOT / "reports/live-tls.json", receipt)
        print(json.dumps(receipt))


if __name__ == "__main__":
    main()
