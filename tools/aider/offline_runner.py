"""Python 3.12 entry for real Aider, with packaged token data and no network.

This guards the registered Repo Map/apply CLI modes. It is not a sandbox for
arbitrary Python supplied by a model. Installation is a separate uv operation.
"""

import hashlib
import json
import os
import socket
import sys
from importlib.metadata import distribution, version
from pathlib import Path

ENCODINGS = {
    "9b5ad71b2ce5302211f9c61530b329a4922fc6a4": "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7",
    "fb374d419588a4632f3f557e76b4b70aebbca790": "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d",
}


def packaged_encodings():
    cache = Path(distribution("litellm").locate_file("litellm/litellm_core_utils/tokenizers"))
    for name, expected in ENCODINGS.items():
        path = cache / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(
                "Aider packaged tokenizer integrity failure; reinstall tools/aider with uv sync --locked"
            )
    return cache


def install_offline_guard():
    def audit(event, args):
        if event.startswith(("socket.getaddrinfo", "socket.gethostby", "socket.getnameinfo")):
            raise PermissionError("Aider local tool network access is disabled")
        if event in {"socket.connect", "socket.sendto", "socket.bind"}:
            if args[0].family in {socket.AF_INET, socket.AF_INET6}:
                raise PermissionError("Aider local tool network access is disabled")

    sys.addaudithook(audit)


def main():
    if sys.version_info[:2] != (3, 12) or version("aider-chat") != "0.86.2":
        raise RuntimeError("Use the pinned Python 3.12 tools/aider environment")
    cache = packaged_encodings()
    os.environ.update(
        CUSTOM_TIKTOKEN_CACHE_DIR=str(cache),
        TIKTOKEN_CACHE_DIR=str(cache),
        LITELLM_LOCAL_MODEL_COST_MAP="True",
        AIDER_ANALYTICS="false",
        DO_NOT_TRACK="1",
    )
    install_offline_guard()
    if sys.argv[1:] == ["--check-local-deps"]:
        import tiktoken

        for name in ("cl100k_base", "o200k_base"):
            assert tiktoken.get_encoding(name).encode("本机编码检查")
        print(
            json.dumps(
                {
                    "aider": "0.86.2",
                    "python": "3.12",
                    "packaged_encodings_verified": True,
                    "network": "disabled",
                }
            )
        )
        return 0
    # Aider accepts a local metadata file. Use the locked package's own data,
    # instead of its otherwise automatic model-price URL lookup.
    metadata = Path(
        distribution("litellm").locate_file("litellm/model_prices_and_context_window_backup.json")
    )
    if (
        hashlib.sha256(metadata.read_bytes()).hexdigest()
        != "e8da995ddcffc05a8dcbe4a8504326a6e352ba9e38151e147cbb5b4b694c937d"
    ):
        raise RuntimeError("Aider packaged model metadata integrity failure")
    sys.argv.extend(["--model-metadata-file", str(metadata)])
    from aider.main import main as aider_main

    return aider_main()


if __name__ == "__main__":
    raise SystemExit(main())
