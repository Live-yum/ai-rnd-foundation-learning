"""Real pinned CPU embeddings -> local HTTP -> AST/Continue/FTS/vector retrieval.

`prepare` explicitly downloads public weights. `serve` loads only checksum-verified
local ONNX/tokenizer files and denies outgoing Python sockets. `verify` runs in the
platform environment; the isolated service needs no platform or model credentials.
"""

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import zipfile
from contextlib import ExitStack
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
WEIGHT_SHA = "6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452"
TOKENIZER_BLOB = "cb202bfe2e3c98645018a6d12f182a434c9d3e02"
MEMBERS = ["onnx/model.onnx", "tokenizer.json"]
SAMPLE_PATHS = [
    "packages/@core/ui-kit/form-ui/src/use-vben-form.ts",
    "packages/@core/ui-kit/form-ui/src/form-api.ts",
    "apps/web-antd/src/views/_core/authentication/login.vue",
]


def check_weights(folder):
    folder = Path(folder)
    weights = (folder / MEMBERS[0]).read_bytes()
    tokenizer = (folder / MEMBERS[1]).read_bytes()
    if hashlib.sha256(weights).hexdigest() != WEIGHT_SHA:
        raise ValueError("Local embedding weights do not match the pinned official ONNX artifact")
    blob = b"blob " + str(len(tokenizer)).encode() + b"\0" + tokenizer
    if hashlib.sha1(blob).hexdigest() != TOKENIZER_BLOB:
        raise ValueError("Local tokenizer does not match the pinned official Git blob")
    return {
        "model": MODEL,
        "revision": REVISION,
        "weights_sha256": WEIGHT_SHA,
        "tokenizer_blob": TOKENIZER_BLOB,
    }


def prepare(folder):
    from huggingface_hub import hf_hub_download

    folder = Path(folder).resolve()
    # This is an explicit installation step, never part of runtime inference.
    for member in MEMBERS:
        cached = hf_hub_download(
            MODEL, member, revision=REVISION, token=False, cache_dir=str(folder / "download-cache")
        )
        target = folder / member
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cached, target)
    print(json.dumps(check_weights(folder)))


def serve(folder, ready):
    evidence = check_weights(folder)
    os.environ.update(
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        HF_HUB_DISABLE_TELEMETRY="1",
        TOKENIZERS_PARALLELISM="false",
    )

    def deny(*args, **kwargs):
        raise RuntimeError("Embedding inference cannot open outgoing network connections")

    socket.socket.connect = deny
    socket.socket.connect_ex = deny
    socket.create_connection = deny
    try:
        socket.create_connection(("example.com", 443))
    except RuntimeError:
        pass
    else:
        raise AssertionError("Embedding egress guard did not reject an outgoing connection")
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer

    tokenizer = Tokenizer.from_file(str(Path(folder) / "tokenizer.json"))
    tokenizer.enable_truncation(max_length=256)
    tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(
        str(Path(folder) / "onnx/model.onnx"),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )
    counts = {"requests": 0, "texts": 0}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, body):
            body = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            self.respond(
                200,
                {
                    **evidence,
                    **counts,
                    "provider": "onnxruntime-cpu",
                    "dimension": 384,
                    "outgoing_python_sockets": "denied",
                },
            )

        def do_POST(self):
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if self.path != "/v1/embeddings" or not 0 < size <= 500000:
                    raise ValueError("Invalid local embedding request")
                body = json.loads(self.rfile.read(size))
                texts = body.get("input")
                if (
                    body.get("model") != MODEL
                    or not isinstance(texts, list)
                    or not 1 <= len(texts) <= 32
                    or any(not isinstance(t, str) or len(t) > 100000 for t in texts)
                ):
                    raise ValueError("Invalid embedding model or batch")
                encoded = tokenizer.encode_batch(texts)
                candidates = {
                    "input_ids": np.asarray([e.ids for e in encoded], dtype=np.int64),
                    "attention_mask": np.asarray(
                        [e.attention_mask for e in encoded], dtype=np.int64
                    ),
                    "token_type_ids": np.asarray([e.type_ids for e in encoded], dtype=np.int64),
                }
                inputs = {item.name: candidates[item.name] for item in session.get_inputs()}
                hidden = session.run(None, inputs)[0]
                mask = candidates["attention_mask"][..., None].astype(np.float32)
                pooled = (hidden * mask).sum(axis=1) / mask.sum(axis=1).clip(min=1e-9)
                vectors = pooled / np.linalg.norm(pooled, axis=1, keepdims=True).clip(min=1e-9)
                if vectors.shape != (len(texts), 384) or not np.isfinite(vectors).all():
                    raise ValueError("Real model returned invalid embeddings")
                counts["requests"] += 1
                counts["texts"] += len(texts)
                self.respond(
                    200,
                    {
                        "model": MODEL,
                        "data": [
                            {"index": i, "embedding": row.tolist()} for i, row in enumerate(vectors)
                        ],
                    },
                )
            except (ValueError, KeyError, TypeError) as exc:
                self.respond(400, {"error": str(exc)})

    server = HTTPServer(("127.0.0.1", 0), Handler)
    Path(ready).write_text(
        json.dumps({"url": f"http://127.0.0.1:{server.server_port}/v1"}), encoding="utf-8"
    )
    try:
        server.serve_forever()
    finally:
        server.server_close()


def verify(folder, interpreter):
    import httpx
    from pydantic import SecretStr

    from workbench.filesystem import sha, write_json
    from workbench.knowledge import build_index
    from workbench.retrieval import add_embeddings, embed, embedding_profile, query
    from workbench.settings import Settings
    from workbench.tools import clean_env, process_options, stop_process
    from workbench.vendor import VENDOR, inventory

    report = {
        "passed": False,
        "inference": "real-public-weights-local-cpu",
        "hosted_inference_calls": 0,
        "sample_scope": "three pinned Vben form/auth files",
    }
    output = ROOT / "reports/local-embeddings.json"
    process = None
    try:
        with (
            tempfile.TemporaryDirectory(prefix="rnd-real-embeddings-") as directory,
            ExitStack() as stack,
        ):
            base = Path(directory)
            ready = base / "ready.json"
            env = clean_env({"HF_HUB_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1"})
            with (base / "server.log").open("w", encoding="utf-8") as log:
                process = subprocess.Popen(
                    [
                        str(Path(interpreter).absolute()),
                        str(Path(__file__).resolve()),
                        "serve",
                        "--weights",
                        str(Path(folder).resolve()),
                        "--ready",
                        str(ready),
                    ],
                    cwd=ROOT,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    **process_options(),
                )
                stack.callback(stop_process, process)
                for _ in range(120):
                    if process.poll() is not None:
                        raise RuntimeError(
                            (base / "server.log").read_text(encoding="utf-8")[-4000:]
                        )
                    if ready.is_file():
                        break
                    time.sleep(0.25)
                else:
                    raise TimeoutError("Local embedding server did not start")
                url = json.loads(ready.read_text(encoding="utf-8"))["url"]
                settings = Settings(
                    _env_file=None,
                    data_dir=base / "data",
                    embedding_base_url=url,
                    embedding_model=MODEL,
                    embedding_api_key=SecretStr("local-no-auth"),
                    embedding_enabled=True,
                    embedding_max_chunks=200,
                    retrieval_engine="continue",
                )
                vectors = embed(
                    embedding_profile(settings),
                    [
                        "How can I reset the form fields?",
                        "Clear all values entered in the form.",
                        "The elephant lives in the African savannah.",
                    ],
                )

                def similarity(a, b):
                    return sum(x * y for x, y in zip(a, b, strict=True))

                related = similarity(vectors[0], vectors[1])
                unrelated = similarity(vectors[0], vectors[2])
                if related <= unrelated + 0.1:
                    raise AssertionError("Real model did not distinguish related form semantics")
                source = base / "source"
                record = next(row for row in inventory() if row["name"] == "yudao-frontend")
                archive = VENDOR / record["archive"]
                if sha(archive) != record["archive_sha256"]:
                    raise ValueError("Pinned Vben archive identity mismatch")
                with zipfile.ZipFile(archive) as z:
                    for name in SAMPLE_PATHS:
                        destination = source / name
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(z.read(name))
                index = base / "index"
                build_index(source, index, record["sha"])
                indexed = add_embeddings(source, index, settings)
                if indexed["embedded"] < 3:
                    raise AssertionError("Actual Vben source chunks were not embedded")
                if add_embeddings(source, index, settings)["embedded"] != 0:
                    raise AssertionError("Unchanged vectors were not reused")
                found = query(
                    source,
                    index,
                    "useVbenForm resetForm validate",
                    limit=8,
                    max_chars=24000,
                    settings=settings,
                )
                if found["mode"] != "ast+continue-fts5+fts5+vector-rrf":
                    raise AssertionError("Actual Continue plus local vector fusion did not execute")
                if not any(row["path"].endswith("use-vben-form.ts") for row in found["matches"]):
                    raise AssertionError("Vben hook missing from real hybrid search")
                scoped = query(source, index, "login", settings=settings, file_suffix=".vue")
                if not scoped["matches"] or any(
                    not r["path"].endswith(".vue") for r in scoped["matches"]
                ):
                    raise AssertionError("Hybrid retrieval escaped the requested Vue source scope")
                changed = source / SAMPLE_PATHS[0]
                changed.write_text(
                    changed.read_text(encoding="utf-8") + "\n// Changed after indexing\n",
                    encoding="utf-8",
                )
                try:
                    query(source, index, "useVbenForm", settings=settings)
                except ValueError as exc:
                    if "源码已改变" not in str(exc):
                        raise
                else:
                    raise AssertionError("Stale source was accepted by hybrid retrieval")
                with httpx.Client(trust_env=False, timeout=5) as client:
                    evidence = client.get(url).raise_for_status().json()
                report.update(
                    passed=True,
                    **evidence,
                    indexed=indexed,
                    semantic_related=related,
                    semantic_unrelated=unrelated,
                    retrieval_mode=found["mode"],
                    source_revision=record["sha"],
                    retrieved_paths=[row["path"] for row in found["matches"]],
                    source_digest=found["source_digest"],
                    cache_reused=True,
                    stale_source_rejected=True,
                    vue_scope_enforced=True,
                )
    except Exception as exc:
        report["error"] = str(exc)[-4000:]
        raise
    finally:
        if process is not None:
            stop_process(process)
        write_json(output, report)
    print(json.dumps(report, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "serve", "verify"])
    parser.add_argument("--weights", type=Path, default=ROOT / ".data/embedding-model")
    parser.add_argument("--ready", type=Path)
    parser.add_argument("--python", default=str(ROOT / "tools/embeddings/.venv/bin/python"))
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.weights)
    elif args.mode == "serve":
        if args.ready is None:
            parser.error("serve requires --ready")
        serve(args.weights, args.ready)
    else:
        verify(args.weights, args.python)


if __name__ == "__main__":
    main()
