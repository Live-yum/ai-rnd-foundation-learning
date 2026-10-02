# workbench/streaming.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：公开模型文本的安全投影与可重放事件流。** 只投影明确schema的根字符串summary/title/explanation，增量始终是待验证草稿。处理UTF-8、JSON转义与跨块密钥前缀，失败清空草稿。SSE订阅读取持久事件，不创建模型调用；刷新先取同一快照的transcript与cursor，再继续之后的事件。

**对应关系：** AuditedEventStream → AssistantStream → Store事件 → /transcript与/stream → Vue消息状态机；最终结构仍须严格校验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**带着一个具体问题阅读：** 服务商把summary分成两段发来时，AssistantStream先提取已完整解码的公开前缀，保存assistant_delta；此刻页面显示草稿。最后整个对象通过schema校验，才写assistant_completed。若后半段不合法，assistant_failed清掉草稿，不能因为用户已经看到一些文字就标成成功。刷新用transcript.cursor续读，而不是再次调用模型。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `public_field`（L24–L32）：接收`schema`。 调用`getattr`、`PUBLIC_FIELDS.get`。 返回路径：L28的`PUBLIC_FIELDS.get(schema.__name__) if getattr(domain, schema.__name__, None) is schema els…`。
- `public_text`（L35–L37）：接收`value`、`schema`。 调用`public_field`、`str`、`getattr`。 返回路径：L37的`str(getattr(value, field, "")) if field else ""`。
- `string_projection`（L40–L82）：接收`source`。 源码说明：Return a decoded prefix and whether its public projection is finished. Finishing the UI projection never finishes provider/schema validation. The audited transport still consumes and validates the com。 控制顺序：L47在`index < len(source)`成立时循环；L49按`char == '"'`分支；L52按`char == "\\"`分支；L53按`index + 1 >= len(source)`分支；L56按`end > len(source)`分支；L62按`len(decoded) == 1 and 0xD800 <= ord(decoded) <= 0xDBFF`分支；L63按`end + 6 > len(source) or source[end : end + 2] != "\\u"`分支；L70按`any(0xD800 <= ord(c) <= 0xDFFF for c in decoded)`分支。后续分支沿下方源码相同行号继续阅读。 调用`len`、`json.loads`、`ord`、`any`、`result.append`、`"".join`。 返回路径：L82的`"".join(result)[:MAX_PUBLIC_TEXT], finished`。
- `string_prefix`（L85–L87）：接收`source`。 源码说明：Decode only complete JSON string characters, including split surrogate pairs.。 调用`string_projection`。 返回路径：L87的`string_projection(source)[0]`。
- `root_string_projection`（L90–L127）：接收`source`、`field`。 源码说明：Find a root string and its projection boundary, never nested fields.。 控制顺序：L92按`not field`分支；L103按`source[position : position + 1] != "{"`分支；L107在`True`成立时循环；L110按`not isinstance(key, str)`分支；L113按`source[position : position + 1] != ":"`分支；L117按`key == field`分支；L118按`source[position : position + 1] != '"'`分支；L123按`source[position : position + 1] != ","`分支。 调用`json.JSONDecoder`、`whitespace`、`decoder.raw_decode`、`isinstance`、`string_projection`。 返回路径：L93的`"", False`；L104的`"", False`；L111的`"", False`。
- `root_string_projection.whitespace`（L97–L100）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L99在`position < len(source) and source[position] in " \r\n\t"`成立时循环。 调用`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `root_string_prefix`（L130–L132）：接收`source`、`field`。 源码说明：Find a root string without interpreting nested fields or unfinished objects.。 调用`root_string_projection`。 返回路径：L132的`root_string_projection(source, field)[0]`。
- `AssistantStream`（L135–L247）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `AssistantStream.__init__`（L138–L169）：接收`store`、`settings`、`run_id`、`response_id`、`stage`、`schema`、`enabled`、`api_key`。 控制顺序：L155按`not self.enabled`分支；L166按`api_key and api_key.get_secret_value()`分支。 调用`callable`、`getattr`、`public_field`、`uuid.uuid4`、`sorted`、`item.get_secret_value`、`vars(settings).values`、`vars`、`isinstance`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AssistantStream.refresh_secrets`（L171–L176）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L173按`lock is not None`分支。 调用`getattr`、`set`、`sorted`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AssistantStream.redact`（L178–L183）：接收`value`。 控制顺序：L181遍历`self.secrets`。 调用`self.settings.redact`、`self.refresh_secrets`、`value.replace`。 返回路径：L183的`value`。
- `AssistantStream.emit`（L185–L187）：接收`kind`、`data`。 控制顺序：L186按`self.enabled`分支。 调用`self.store.assistant_event`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AssistantStream.mode`（L189–L191）：接收`transport`。 调用`self.emit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AssistantStream.content`（L193–L232）：接收`fragment`。 控制顺序：L194按`not self.enabled or not self.field or self.projection_finished`分支；L198按`self.projection_finished`分支；L205遍历`self.secrets`；L206遍历`range(1, min(len(secret), len(projected) + 1))`；L207按`projected.endswith(secret[:size])`分支；L209按`hold`分支；L213在`True`成立时循环；L215遍历`self.secrets`。后续分支沿下方源码相同行号继续阅读。 调用`root_string_projection`、`self.redact`、`range`、`min`、`len`、`projected.endswith`、`max`、`projected.find`、`safe.startswith`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AssistantStream.failed`（L234–L239）：接收`code`。 调用`self.emit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `AssistantStream.completed_data`（L241–L247）：接收`value`、`schema`。 调用`self.redact`、`public_text`。 返回路径：L242的`{ **self.data, "content": self.redact(public_text(value, schema))[:MAX_PUBLIC_TEXT], "vali…`。
- `sse_event`（L250–L256）：接收`event`。 调用`json.dumps`。 返回路径：L251的`f"id: {event['id']}\nevent: {event['kind']}\n" + "data: " + json.dumps(event, ensure_ascii…`。
- `event_stream`（L259–L287）：接收`request`、`store`、`run_id`、`after`、`interval`。 源码说明：Replay first, then tail committed events; cancellation only closes this iterator.。 控制顺序：L263在`not await request.is_disconnected()`成立时循环；L265遍历`events`；L266按`await request.is_disconnected()`分支；L270按`events`分支；L274按`run["status"] not in {"QUEUED", "RUNNING"}`分支；L276按`await asyncio.to_thread(store.events, run_id, cursor)`分支；L285按`idle_ticks % 40 == 0`分支。 调用`request.is_disconnected`、`asyncio.to_thread`、`sse_event`、`json.dumps`、`asyncio.sleep`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `register_streaming_routes`（L290–L323）：接收`app`、`auth`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `register_streaming_routes.transcript`（L292–L293）：接收`run_id`、`store`。 调用`Depends`、`store.transcript`、`app.get`。 返回路径：L293的`store.transcript(run_id)`。
- `register_streaming_routes.stream`（L296–L323）：接收`request`、`run_id`、`after`、`last_event_id`、`store`。 控制顺序：L304按`last_event_id is not None`分支；L305按`not last_event_id.isascii() or not last_event_id.isdecimal() or len(last_event_id) > …`分支；L310抛异常，停止当前正常路径；L312按`value > 9223372036854775807`分支；L313抛异常，停止当前正常路径。 调用`Query`、`Header`、`Depends`、`store.get_run`、`last_event_id.isascii`、`last_event_id.isdecimal`、`len`、`HTTPException`、`int`等。 返回路径：L315的`StreamingResponse( event_stream(request, store, run_id, after), media_type="text/event-str…`。

</details>

**创建路径：** `workbench/streaming.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L323。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11535`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/streaming.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b9b2f71a7a663ef4401ea3f674650c6bd68cf0bb61a4224fb12d48fa5296a5ab"} -->
````python
# workbench/streaming.py
"""Durable, authenticated UI streams. A subscriber never owns the model worker.

Only a schema's explicitly user-facing root string is projected. Partial text is
always a draft; executable/schema data is available only after strict validation.
"""

import asyncio
import json
import uuid

from fastapi import Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import SecretStr

PUBLIC_FIELDS = {
    "Requirement": "summary",
    "Plan": "title",
    "Patches": "explanation",
    "ModelReview": "summary",
}
MAX_PUBLIC_TEXT = 20000


def public_field(schema):
    # Identity, rather than an arbitrary schema with the same name, is intentional.
    from workbench import domain

    return (
        PUBLIC_FIELDS.get(schema.__name__)
        if getattr(domain, schema.__name__, None) is schema
        else None
    )


def public_text(value, schema):
    field = public_field(schema)
    return str(getattr(value, field, "")) if field else ""


def string_projection(source):
    """Return a decoded prefix and whether its public projection is finished.

    Finishing the UI projection never finishes provider/schema validation. The
    audited transport still consumes and validates the complete response.
    """
    result, index, finished = [], 0, False
    while index < len(source):
        char = source[index]
        if char == '"':
            finished = True
            break
        if char == "\\":
            if index + 1 >= len(source):
                break
            end = index + (6 if source[index + 1] == "u" else 2)
            if end > len(source):
                break
            try:
                decoded = json.loads('"' + source[index:end] + '"')
            except ValueError:
                break
            if len(decoded) == 1 and 0xD800 <= ord(decoded) <= 0xDBFF:
                if end + 6 > len(source) or source[end : end + 2] != "\\u":
                    break
                try:
                    decoded = json.loads('"' + source[index : end + 6] + '"')
                except ValueError:
                    break
                end += 6
            if any(0xD800 <= ord(c) <= 0xDFFF for c in decoded):
                break
            result.append(decoded)
            index = end
        else:
            if ord(char) < 0x20 or 0xD800 <= ord(char) <= 0xDFFF:
                break
            result.append(char)
            index += 1
        if len(result) >= MAX_PUBLIC_TEXT:
            finished = True
            break
    return "".join(result)[:MAX_PUBLIC_TEXT], finished


def string_prefix(source):
    """Decode only complete JSON string characters, including split surrogate pairs."""
    return string_projection(source)[0]


def root_string_projection(source, field):
    """Find a root string and its projection boundary, never nested fields."""
    if not field:
        return "", False
    decoder = json.JSONDecoder()
    position = 0

    def whitespace():
        nonlocal position
        while position < len(source) and source[position] in " \r\n\t":
            position += 1

    whitespace()
    if source[position : position + 1] != "{":
        return "", False
    position += 1
    try:
        while True:
            whitespace()
            key, position = decoder.raw_decode(source, position)
            if not isinstance(key, str):
                return "", False
            whitespace()
            if source[position : position + 1] != ":":
                return "", False
            position += 1
            whitespace()
            if key == field:
                if source[position : position + 1] != '"':
                    return "", False
                return string_projection(source[position + 1 :])
            _, position = decoder.raw_decode(source, position)
            whitespace()
            if source[position : position + 1] != ",":
                return "", False
            position += 1
    except ValueError, RecursionError:
        return "", False


def root_string_prefix(source, field):
    """Find a root string without interpreting nested fields or unfinished objects."""
    return root_string_projection(source, field)[0]


class AssistantStream:
    """A single real response attempt. Events contain neither prompts nor raw JSON."""

    def __init__(
        self, store, settings, run_id, response_id, stage, schema, enabled, *, api_key=None
    ):
        self.store, self.settings, self.run_id = store, settings, run_id
        self.enabled = enabled and callable(getattr(store, "assistant_event", None))
        self.field = public_field(schema)
        self.raw = ""
        self.projection_finished = False
        self.sent = ""
        self.data = {
            "message_id": uuid.uuid4().hex,
            "response_id": response_id,
            "stage": stage,
            "validation": "pending",
            "transport": "pending",
        }
        self.secrets = []
        if not self.enabled:
            return
        self.secrets = sorted(
            {
                item.get_secret_value()
                for item in vars(settings).values()
                if isinstance(item, SecretStr) and item.get_secret_value()
            },
            key=len,
            reverse=True,
        )
        if api_key and api_key.get_secret_value():
            self.secrets.append(api_key.get_secret_value())
        self.refresh_secrets()
        self.emit("assistant_start", self.data)

    def refresh_secrets(self):
        lock = getattr(self.settings, "_model_keys_lock", None)
        if lock is not None:
            with lock:
                known = set(getattr(self.settings, "_model_keys", ()))
            self.secrets = sorted(set(self.secrets) | known, key=len, reverse=True)

    def redact(self, value):
        value = self.settings.redact(value)
        self.refresh_secrets()
        for secret in self.secrets:
            value = value.replace(secret, "[redacted]")
        return value

    def emit(self, kind, data):
        if self.enabled:
            self.store.assistant_event(self.run_id, kind, data)

    def mode(self, transport):
        self.data["transport"] = transport
        self.emit("assistant_status", {**self.data, "status": "receiving"})

    def content(self, fragment):
        if not self.enabled or not self.field or self.projection_finished:
            return
        self.raw += fragment
        projected, self.projection_finished = root_string_projection(self.raw, self.field)
        if self.projection_finished:
            # Later private patch/plan content is still audited in full, but no
            # longer retained or reparsed by this user-facing projection.
            self.raw = ""
        # A known credential split across chunks must never be emitted piecemeal.
        safe = self.redact(projected)
        hold = 0
        for secret in self.secrets:
            for size in range(1, min(len(secret), len(projected) + 1)):
                if projected.endswith(secret[:size]):
                    hold = max(hold, size)
        if hold:
            boundary = len(projected) - hold
            # Overlapping complete/partial credentials cannot expose a prefix of
            # a complete credential while waiting for the remaining suffix.
            while True:
                previous = boundary
                for secret in self.secrets:
                    # Use the earliest full occurrence crossing this boundary.
                    # An overlapping occurrence can cross a newly shortened
                    # boundary too, so repeat until no credential is bisected.
                    offset = projected.find(
                        secret,
                        max(0, boundary - len(secret) + 1),
                        boundary + len(secret),
                    )
                    if offset >= 0 and offset < boundary < offset + len(secret):
                        boundary = offset
                if boundary == previous:
                    break
            safe = self.redact(projected[:boundary])
        if safe.startswith(self.sent) and len(safe) > len(self.sent):
            delta = safe[len(self.sent) :]
            self.sent = safe
            self.emit("assistant_delta", {**self.data, "text": delta})

    def failed(self, code):
        # Static error codes only. A failed draft must not be presented as a result.
        self.emit(
            "assistant_failed",
            {**self.data, "validation": "failed", "status": "failed", "code": code, "content": ""},
        )

    def completed_data(self, value, schema):
        return {
            **self.data,
            "content": self.redact(public_text(value, schema))[:MAX_PUBLIC_TEXT],
            "validation": "validated",
            "status": "completed",
        }


def sse_event(event):
    return (
        f"id: {event['id']}\nevent: {event['kind']}\n"
        + "data: "
        + json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        + "\n\n"
    )


async def event_stream(request, store, run_id, after, *, interval=0.25):
    """Replay first, then tail committed events; cancellation only closes this iterator."""
    cursor = after
    idle_ticks = 0
    while not await request.is_disconnected():
        events = await asyncio.to_thread(store.events, run_id, cursor)
        for event in events:
            if await request.is_disconnected():
                return
            cursor = event["id"]
            yield sse_event(event)
        if events:
            idle_ticks = 0
            continue
        run = await asyncio.to_thread(store.get_run, run_id)
        if run["status"] not in {"QUEUED", "RUNNING"}:
            # A finish transaction may have committed between events() and get_run().
            if await asyncio.to_thread(store.events, run_id, cursor):
                continue
            yield (
                "event: idle\ndata: "
                + json.dumps({"cursor": cursor, "status": run["status"]}, ensure_ascii=False)
                + "\n\n"
            )
            return
        idle_ticks += 1
        if idle_ticks % 40 == 0:
            yield ": keep-alive\n\n"
        await asyncio.sleep(interval)


def register_streaming_routes(app, auth):
    @app.get("/runs/{run_id}/transcript")
    def transcript(run_id: str, store=Depends(auth)):
        return store.transcript(run_id)

    @app.get("/runs/{run_id}/stream")
    def stream(
        request: Request,
        run_id: str,
        after: int = Query(default=0, ge=0, le=9223372036854775807),
        last_event_id: str | None = Header(default=None),
        store=Depends(auth),
    ):
        store.get_run(run_id)
        if last_event_id is not None:
            if (
                not last_event_id.isascii()
                or not last_event_id.isdecimal()
                or len(last_event_id) > 19
            ):
                raise HTTPException(422, "Last-Event-ID 必须是非负事件编号")
            value = int(last_event_id)
            if value > 9223372036854775807:
                raise HTTPException(422, "Last-Event-ID 超出范围")
            after = max(after, value)
        return StreamingResponse(
            event_stream(request, store, run_id, after),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-store",
                "X-Accel-Buffering": "no",
                "Referrer-Policy": "no-referrer",
            },
        )
````
