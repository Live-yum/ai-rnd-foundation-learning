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
