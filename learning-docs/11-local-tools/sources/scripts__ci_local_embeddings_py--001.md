# scripts/ci_local_embeddings.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：固定真实权重的本机推理验收和服务。** prepare显式下载校验后的公开模型；serve在回环HTTP上用CPU推理且拒绝出站套接字；verify启动自有服务、取固定Vben样本、查缓存及真实融合检索，最后关闭服务。

**对应关系：** 独立tools/embeddings解释器 + 平台retrieval → local-embeddings.json。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `check_weights`（L35–L49）：接收`folder`。 控制顺序：L39按`hashlib.sha256(weights).hexdigest() != WEIGHT_SHA`分支；L40抛异常，停止当前正常路径；L42按`hashlib.sha1(blob).hexdigest() != TOKENIZER_BLOB`分支；L43抛异常，停止当前正常路径。 调用`Path`、`(folder / MEMBERS[0]).read_bytes`、`(folder / MEMBERS[1]).read_bytes`、`hashlib.sha256(weights).hexdigest`、`hashlib.sha256`、`ValueError`、`str(len(tokenizer)).encode`、`str`、`len`等。 返回路径：L44的`{ "model": MODEL, "revision": REVISION, "weights_sha256": WEIGHT_SHA, "tokenizer_blob": TO…`。
- `prepare`（L52–L64）：接收`folder`。 控制顺序：L57遍历`MEMBERS`。 调用`Path(folder).resolve`、`Path`、`hf_hub_download`、`str`、`target.parent.mkdir`、`shutil.copyfile`、`print`、`json.dumps`、`check_weights`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `serve`（L67–L179）：接收`folder`、`ready`。 控制顺序：L87抛异常，停止当前正常路径。 调用`check_weights`、`os.environ.update`、`socket.create_connection`、`AssertionError`、`Tokenizer.from_file`、`str`、`Path`、`tokenizer.enable_truncation`、`tokenizer.enable_padding`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `serve.deny`（L76–L77）：接收`*args`、`**kwargs`。 控制顺序：L77抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `serve.Handler`（L105–L170）：继承`BaseHTTPRequestHandler`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `serve.Handler.log_message`（L106–L107）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `serve.Handler.respond`（L109–L115）：接收`status`、`body`。 调用`json.dumps(body).encode`、`json.dumps`、`self.send_response`、`self.send_header`、`str`、`len`、`self.end_headers`、`self.wfile.write`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `serve.Handler.do_GET`（L117–L127）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.respond`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `serve.Handler.do_POST`（L129–L170）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L132按`self.path != "/v1/embeddings" or not 0 < size <= 500000`分支；L133抛异常，停止当前正常路径；L136按`body.get("model") != MODEL or not isinstance(texts, list) or not 1 <= len(texts) <= 3…`分支；L142抛异常，停止当前正常路径；L156按`vectors.shape != (len(texts), 384) or not np.isfinite(vectors).all()`分支；L157抛异常，停止当前正常路径。 调用`int`、`self.headers.get`、`ValueError`、`json.loads`、`self.rfile.read`、`body.get`、`isinstance`、`len`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify`（L182–L333）：接收`folder`、`interpreter`。 控制顺序：L227遍历`range(120)`；L228按`process.poll() is not None`分支；L229抛异常，停止当前正常路径；L232按`ready.is_file()`分支；L236抛异常，停止当前正常路径；L262按`related <= unrelated + 0.1`分支；L263抛异常，停止当前正常路径；L267按`sha(archive) != record["archive_sha256"]`分支。后续分支沿下方源码相同行号继续阅读。 调用`tempfile.TemporaryDirectory`、`ExitStack`、`Path`、`clean_env`、`(base / "server.log").open`、`subprocess.Popen`、`str`、`Path(interpreter).absolute`、`Path(__file__).resolve`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify.similarity`（L257–L258）：接收`a`、`b`。 调用`sum`、`zip`。 返回路径：L258的`sum(x * y for x, y in zip(a, b, strict=True))`。
- `main`（L336–L350）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L343按`args.mode == "prepare"`分支；L345按`args.mode == "serve"`分支；L346按`args.ready is None`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`str`、`parser.parse_args`、`prepare`、`parser.error`、`serve`、`verify`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_local_embeddings.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L354。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14573`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_local_embeddings.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7d2068cb8d2d2921a1ac56dfc80b8eba17deff770e34f01a69fd2f7531bd65d7"} -->
````python
# scripts/ci_local_embeddings.py
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
````
