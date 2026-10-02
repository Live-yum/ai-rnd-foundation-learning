# ui/tests/protocol.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/protocol.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L233。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7755`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/protocol.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "941a7704838e8fff78cfb83436443351cb4dc236cc157ceb9ed84dbe6e3175c1"} -->
````typescript
// ui/tests/protocol.test.ts
import { describe, it, expect, vi, afterEach } from 'vitest'
import { api, ApiError, SSEParser, readStream, setToken } from '../src/api'
import {
  applyMessageEvent,
  canAct,
  gatePayload,
  gateIdentity,
  statusLabel,
  activeStage,
} from '../src/presentation'
import type { ChatMessage, Gate, Run } from '../src/types'
const gate: Gate = {
  gate_id: 'a'.repeat(64),
  version: 2,
  digest: 'b'.repeat(64),
  stage: 'requirements',
  data: {},
  actions: ['approve', 'revise', 'reject'],
  can_approve: true,
}
afterEach(() => {
  setToken('')
  vi.unstubAllGlobals()
})
describe('incremental authenticated SSE protocol', () => {
  it('parses arbitrary partial CRLF, comments and multiline data', () => {
    const parser = new SSEParser()
    expect(parser.push(': heartbeat\r\n\r\nid: 42\r')).toEqual([])
    expect(parser.push('\nevent: status\r\ndata: first\r\ndata: second\r\n\r\n')).toEqual([
      { id: 42, event: 'status', data: 'first\nsecond' },
    ])
  })
  it('retains unfinished frame and ignores comment-only frames', () => {
    const p = new SSEParser()
    expect(p.push(': hi\n\ndata: {"a":')).toEqual([])
    expect(p.push('1}\n\n')).toEqual([{ id: undefined, event: undefined, data: '{"a":1}' }])
  })
  it('does not accept invalid event ids', () => {
    const p = new SSEParser()
    expect(p.push('id: not-a-number\ndata: {}\n\n')[0].id).toBeUndefined()
  })
  it('uses Authorization and Last-Event-ID, never token URL or storage', async () => {
    setToken('private-test-token')
    const event = { id: 8, kind: 'assistant_delta', data: { message_id: 'm1', text: '中文 🧪' } }
    const bytes = new TextEncoder().encode(
      `id: 8\ndata: ${JSON.stringify(event)}\n\nevent: idle\ndata: {"cursor":8}\n\n`,
    )
    const response = new Response(
      new ReadableStream({
        start(c) {
          for (const byte of bytes) c.enqueue(new Uint8Array([byte]))
          c.close()
        },
      }),
      { headers: { 'content-type': 'text/event-stream' } },
    )
    const fetchMock = vi.fn().mockResolvedValue(response)
    vi.stubGlobal('fetch', fetchMock)
    const events: any[] = []
    const result = await readStream(
      'run-1',
      7,
      new AbortController().signal,
      (e) => events.push(e),
      () => {},
    )
    expect(result.idle).toBe(true)
    expect(events).toEqual([event])
    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/runs/run-1/stream?after=7')
    expect(options.headers.Authorization).toBe('Bearer private-test-token')
    expect(options.headers['Last-Event-ID']).toBe('7')
    expect(JSON.stringify({ ...localStorage, ...sessionStorage })).not.toContain(
      'private-test-token',
    )
  })
  it('reports HTTP failure without echoing validation input', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: [{ loc: ['body', 'api_key'], msg: 'Invalid value', input: 'private-secret' }],
          }),
          { status: 422 },
        ),
      ),
    )
    await expect(api('/settings/models')).rejects.toThrow('api_key：Invalid value')
    try {
      await api('/settings/models')
    } catch (e) {
      expect(String(e)).not.toContain('private-secret')
    }
  })
  it('rejects unexpected non-SSE content', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValue(
          new Response('not SSE', { headers: { 'content-type': 'application/json' } }),
        ),
    )
    await expect(
      readStream(
        'run',
        0,
        new AbortController().signal,
        () => {},
        () => {},
      ),
    ).rejects.toThrow('服务未返回事件流')
  })
})
describe('message reducer and authoritative gate identity', () => {
  it('appends only deltas then replaces with validated final content', () => {
    const messages: ChatMessage[] = []
    applyMessageEvent(messages, {
      id: 1,
      kind: 'assistant_start',
      data: {
        message_id: 'm',
        stage: 'requirements',
        validation: 'pending',
        transport: 'streaming',
      },
    })
    applyMessageEvent(messages, {
      id: 2,
      kind: 'assistant_delta',
      data: { message_id: 'm', text: '你好' },
    })
    applyMessageEvent(messages, {
      id: 3,
      kind: 'assistant_delta',
      data: { message_id: 'm', text: '，世界' },
    })
    expect(messages[0].content).toBe('你好，世界')
    applyMessageEvent(messages, {
      id: 4,
      kind: 'assistant_completed',
      data: {
        message_id: 'm',
        content: '你好，世界',
        validation: 'validated',
        status: 'completed',
      },
    })
    expect(messages).toHaveLength(1)
    expect(messages[0]).toMatchObject({
      content: '你好，世界',
      validation: 'validated',
      status: 'completed',
    })
  })
  it('does not expose raw JSON, reasoning or unrelated event fields', () => {
    const messages: ChatMessage[] = []
    applyMessageEvent(messages, {
      id: 1,
      kind: 'assistant_delta',
      data: { message_id: 'm', text: 'visible', reasoning_content: 'hidden' },
    })
    expect(JSON.stringify(messages)).not.toContain('hidden')
    applyMessageEvent(messages, {
      id: 2,
      kind: 'status',
      data: { message_id: 'other', text: 'ignore' },
    })
    expect(messages).toHaveLength(1)
  })
  it('marks failed validation and keeps server final public content', () => {
    const messages: ChatMessage[] = []
    applyMessageEvent(messages, {
      id: 1,
      kind: 'assistant_failed',
      data: { message_id: 'm', content: '保留摘要', validation: 'failed' },
    })
    expect(messages[0]).toMatchObject({
      content: '保留摘要',
      status: 'failed',
      validation: 'failed',
    })
  })
  it('includes version, digest and explicit approval boolean', () => {
    expect(gatePayload(gate, 'approve')).toEqual({
      gate_id: gate.gate_id,
      version: 2,
      digest: gate.digest,
      action: 'approve',
      approved: true,
    })
    expect(gatePayload(gate, 'reject').approved).toBe(false)
  })
  it('does not enable approval for missing identity or blocking conditions', () => {
    const run = { pending: gate } as Run
    expect(canAct(run, 'approve')).toBe(true)
    expect(canAct({ pending: { ...gate, can_approve: false } } as Run, 'approve')).toBe(false)
    expect(canAct({ pending: { ...gate, digest: '' } } as Run, 'approve')).toBe(false)
    expect(canAct(run, 'answer')).toBe(false)
  })
  it('distinguishes every gate version and source delivery label', () => {
    expect(gateIdentity(gate)).not.toBe(gateIdentity({ ...gate, version: 3 }))
    expect(statusLabel('READY')).toBe('运行级交付')
    expect(statusLabel('SOURCE_READY')).toBe('源码级交付')
  })
  it.each([
    ['planning', 1],
    ['coding', 3],
    ['review', 4],
  ])('maps a live %s model stage when no workflow event exists', (stage, expected) => {
    expect(
      activeStage({ status: 'RUNNING' } as Run, [
        { id: 1, kind: 'assistant_start', data: { stage } },
      ]),
    ).toBe(expected)
  })
  it('keeps the latest workflow stage authoritative during model streaming', () => {
    expect(
      activeStage({ status: 'RUNNING' } as Run, [
        { id: 1, kind: 'stage', data: { name: 'verify', phase: 'started' } },
        { id: 2, kind: 'assistant_delta', data: { stage: 'coding', text: '公开摘要' } },
      ]),
    ).toBe(4)
  })
  it('keeps an early rejection at its actual stage instead of claiming delivery', () => {
    expect(
      activeStage({ status: 'REJECTED' } as Run, [
        { id: 1, kind: 'stage', data: { name: 'requirements', phase: 'completed' } },
      ]),
    ).toBe(0)
  })
})
````
