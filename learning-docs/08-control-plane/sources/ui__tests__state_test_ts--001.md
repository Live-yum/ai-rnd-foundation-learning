# ui/tests/state.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/state.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L83。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2899`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/state.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7d42b43c888f55eba935b743050a2042ecc017410cb1840a1b08fff236f94c12"} -->
````typescript
// ui/tests/state.test.ts
import { afterEach, describe, expect, it, vi } from 'vitest'
import { connect, state, lock, mutationKey, clearMutationKey, refreshLists } from '../src/state'
import { hasToken } from '../src/api'
afterEach(() => {
  lock()
  vi.unstubAllGlobals()
})
describe('workspace state safety', () => {
  it('keeps a valid authenticated workspace when model configuration is unreadable', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async (url: string) =>
          new Response(
            JSON.stringify(
              url === '/catalog'
                ? []
                : url === '/projects'
                  ? [{ id: 'p', title: '真实项目' }]
                  : url === '/runs'
                    ? []
                    : { detail: '配置文件权限不正确' },
            ),
            {
              status: url === '/models' || url === '/settings/models' ? 503 : 200,
              headers: { 'content-type': 'application/json' },
            },
          ),
      ),
    )
    await connect('test-token')
    expect(state.authenticated).toBe(true)
    expect(hasToken()).toBe(true)
    expect(state.projects[0].title).toBe('真实项目')
    expect(state.settings).toBeNull()
    expect(state.notice).toContain('新模型工作已禁用')
  })
  it('invalid authentication clears the in-memory token', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response('{"detail":"需要令牌"}', { status: 401 })),
    )
    await expect(connect('invalid')).rejects.toThrow()
    expect(hasToken()).toBe(false)
    expect(state.authenticated).toBe(false)
  })
  it('preserves one idempotency key until an action is definitively accepted', () => {
    const first = mutationKey('answer:gate1')
    expect(mutationKey('answer:gate1')).toBe(first)
    expect(mutationKey('answer:gate2')).not.toBe(first)
    clearMutationKey('answer:gate1')
    expect(mutationKey('answer:gate1')).not.toBe(first)
  })
  it('does not repopulate private state from a delayed refresh after Lock', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async (url: string) =>
          new Response(JSON.stringify(url === '/settings/models' ? { ready: true } : [])),
      ),
    )
    await connect('test-token')
    let release!: (value: Response) => void
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string) =>
        url === '/projects'
          ? new Promise<Response>((resolve) => {
              release = resolve
            })
          : Promise.resolve(new Response('[]')),
      ),
    )
    const pending = refreshLists()
    lock()
    release(new Response(JSON.stringify([{ id: 'private-project', title: '不应再次展示' }])))
    await pending
    expect(state.authenticated).toBe(false)
    expect(state.projects).toEqual([])
    expect(state.settings).toBeNull()
    expect(hasToken()).toBe(false)
  })
})
````
