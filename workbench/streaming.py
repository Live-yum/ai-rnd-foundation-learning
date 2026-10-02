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
