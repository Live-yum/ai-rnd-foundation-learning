import type { RunEvent } from './types'
let accessToken = ''
export function setToken(value: string) {
  accessToken = value.trim()
}
export function hasToken() {
  return !!accessToken
}
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}
export function errorText(error: unknown) {
  return error instanceof Error ? error.message : '请求失败，请重新连接后再试'
}
export function isAbort(error: unknown) {
  return error instanceof DOMException && error.name === 'AbortError'
}
function headers(json = false, key?: string) {
  return {
    Authorization: `Bearer ${accessToken}`,
    ...(json ? { 'Content-Type': 'application/json' } : {}),
    ...(key ? { 'Idempotency-Key': key } : {}),
  }
}
async function check(response: Response) {
  if (response.ok) return response
  let detail: unknown
  try {
    detail = (await response.json()).detail
  } catch {
    detail = undefined
  }
  // Do not echo arbitrary request bodies, credentials, or validation input values.
  const message =
    typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail
            .map((d) => `${d.loc?.slice(1).join('.') || '输入'}：${d.msg || '格式不正确'}`)
            .join('；')
        : `服务返回 ${response.status}`
  throw new ApiError(response.status, message)
}
export async function api<T = any>(
  path: string,
  options: { method?: string; body?: unknown; signal?: AbortSignal; key?: string } = {},
): Promise<T> {
  const response = await fetch(path, {
    method: options.method || 'GET',
    headers: headers(options.body !== undefined, options.key),
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    signal: options.signal,
    cache: 'no-store',
    credentials: 'omit',
  })
  await check(response)
  return response.status === 204 ? (undefined as T) : response.json()
}
export async function downloadRun(runId: string) {
  const response = await check(
    await fetch(`/runs/${encodeURIComponent(runId)}/download`, {
      headers: headers(),
      cache: 'no-store',
      credentials: 'omit',
    }),
  )
  const url = URL.createObjectURL(await response.blob()),
    link = document.createElement('a')
  link.href = url
  link.download = `${runId}.zip`
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
export interface SSEFrame {
  id?: number
  event?: string
  data: string
}
/** Incremental SSE parser. Handles UTF-8 chunks, CRLF, comments, multiline data and partial frames. */
export class SSEParser {
  private buffer = ''
  private lines: string[] = []
  push(chunk: string): SSEFrame[] {
    this.buffer += chunk
    const frames: SSEFrame[] = []
    let i: number
    while ((i = this.buffer.indexOf('\n')) >= 0) {
      const line = this.buffer.slice(0, i).replace(/\r$/, '')
      this.buffer = this.buffer.slice(i + 1)
      if (line === '') {
        const frame = this.frame()
        if (frame) frames.push(frame)
        this.lines = []
      } else this.lines.push(line)
    }
    return frames
  }
  private frame(): SSEFrame | null {
    let id: number | undefined, event: string | undefined
    const data: string[] = []
    for (const line of this.lines) {
      if (line.startsWith(':')) continue
      const i = line.indexOf(':'),
        field = i < 0 ? line : line.slice(0, i),
        value = i < 0 ? '' : line.slice(i + 1).replace(/^ /, '')
      if (field === 'data') data.push(value)
      if (field === 'event') event = value
      if (field === 'id' && /^\d+$/.test(value)) id = Number(value)
    }
    return data.length ? { id, event, data: data.join('\n') } : null
  }
}
export async function readStream(
  runId: string,
  after: number,
  signal: AbortSignal,
  onEvent: (event: RunEvent) => void,
  onOpen: () => void,
) {
  const response = await check(
    await fetch(`/runs/${encodeURIComponent(runId)}/stream?after=${after}`, {
      headers: {
        ...headers(),
        Accept: 'text/event-stream',
        ...(after ? { 'Last-Event-ID': String(after) } : {}),
      },
      signal,
      cache: 'no-store',
      credentials: 'omit',
    }),
  )
  if (!response.body) throw new Error('浏览器不支持流式响应')
  if (!response.headers.get('content-type')?.includes('text/event-stream'))
    throw new Error('服务未返回事件流')
  onOpen()
  let idle = false
  const reader = response.body.getReader(),
    decoder = new TextDecoder(),
    parser = new SSEParser()
  try {
    while (!signal.aborted) {
      const { value, done } = await reader.read()
      if (done) break
      for (const frame of parser.push(decoder.decode(value, { stream: true }))) {
        if (frame.event === 'idle') {
          idle = true
          continue
        }
        let parsed: any
        try {
          parsed = JSON.parse(frame.data)
        } catch {
          continue
        }
        if (
          parsed &&
          typeof parsed.kind === 'string' &&
          Number.isSafeInteger(parsed.id ?? frame.id)
        )
          onEvent({ ...parsed, id: parsed.id ?? frame.id })
      }
    }
  } finally {
    await reader.cancel().catch(() => {})
    reader.releaseLock()
  }
  return { idle }
}
