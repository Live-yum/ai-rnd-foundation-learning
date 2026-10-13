# Explicitly authorized public test CA

The user authorized committing `caddy-root.pem` on 2026-10-11 for the test client
of `https://170.106.181.109:8317/v1` only. It contains one public CERTIFICATE,
no private key. Source: reviewed Git blob `5f74599575e83c730b7f30dc1482bf343ad1c19f`.

SHA256 certificate fingerprint:
`15:DB:86:A8:D1:15:66:62:5D:42:20:51:59:91:72:7C:90:0E:23:2E:64:1D:8E:7F:CB:08:B0:B4:2D:30:79:AF`.

Subject: `CN=Caddy Local Authority - 2026 ECC Root`. Self-signature verified.
Validity: 2026-10-11 02:59:32 UTC through 2036-08-19 02:59:32 UTC.
This root does not prove the live leaf certificate has the correct IP SAN.

Only `scripts/live_test_client.py` loads it into a scoped SSLContext after checking
the fingerprint and exact endpoint. Host/IP verification and certificate-chain
validation remain enabled. The transport allows only this service's model probe
and Chat Completions paths. It never installs a system root, changes proxy
settings, follows redirects, or disables TLS verification.

The user's no-charge declaration is recorded separately from TLS trust. Paid
mode still requires a positive explicit ceiling and conservative tariff; free
mode requires explicit acknowledgement and exact endpoint binding. Request,
step, token and duration limits continue to apply.
