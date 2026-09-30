"""User-authorized exact Hello request; never print credentials or raw HTTP errors."""

import json
import os
import re
import sys
import urllib.error
import urllib.request


def main():
    if (
        os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
        or os.environ.get("GITHUB_REPOSITORY") != "Live-yum/ai-rnd-foundation-learning"
        or os.environ.get("GITHUB_REF") != "refs/heads/feat/real-model-acceptance"
    ):
        print(json.dumps({"passed": False, "error": "untrusted_manual_context"}))
        return 1
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if (
        not key
        or os.environ.get("BASE_URL", "").rstrip("/") != "https://api.deepseek.com"
        or os.environ.get("MODE") != "deepseek-flash"
    ):
        print(json.dumps({"passed": False, "error": "missing_or_mismatched_rnd_configuration"}))
        return 1
    payload = {
        "model": "deepseek-flash",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high",
        "stream": False,
    }
    request = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST",
    )

    # No redirects: credentials cannot be forwarded to a different endpoint.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=120) as response:
            status = response.status
            raw = response.read(1048577)
        if len(raw) > 1048576:
            raise ValueError("response_too_large")
        body = json.loads(raw)
        content = body["choices"][0]["message"]["content"]
        passed = status == 200 and isinstance(content, str) and bool(content.strip())
        print(
            json.dumps(
                {
                    "passed": passed,
                    "http_status": status,
                    "valid_reply": passed,
                    "model": "deepseek-flash",
                    "thinking": "enabled",
                    "reasoning_effort": "high",
                }
            )
        )
        return 0 if passed else 1
    except urllib.error.HTTPError as error:
        code = "provider_http_error"
        try:
            value = json.loads(error.read(65536)).get("error", {}).get("code")
            if (
                isinstance(value, str)
                and re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", value)
                and key not in value
            ):
                code = value
        except Exception:
            pass
        print(json.dumps({"passed": False, "http_status": error.code, "error": code}))
        return 1
    except Exception as error:
        print(json.dumps({"passed": False, "error_type": type(error).__name__}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
