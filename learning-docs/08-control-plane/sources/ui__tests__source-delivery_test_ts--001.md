# ui/tests/source-delivery.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/source-delivery.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L66。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2647`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/source-delivery.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3597f2b7c3ec69f64a623fe77f244a4ee909aaaadc669a86ac0de79a95937686"} -->
````typescript
// ui/tests/source-delivery.test.ts
import { describe, expect, it } from 'vitest'
import { milestoneStatus, sourceDeliveryState, runNextAction } from '../src/presentation'
import type { Run } from '../src/types'

const run: Run = {
  id: 'candidate',
  project_id: 'project',
  status: 'SOURCE_READY',
  template: 'native',
  auto_mode: false,
}

describe('source candidate presentation', () => {
  it('treats missing metadata conservatively without breaking legacy records', () => {
    expect(sourceDeliveryState(run).sourceOnly).toBe(true)
    expect(sourceDeliveryState(run).title).toBe('代码已保留，未经运行验证')
    expect(sourceDeliveryState({ ...run, status: 'READY' }).sourceOnly).toBe(false)
    expect(runNextAction(run)).toContain('源码可下载')
  })

  it.each([
    ['complete', 'unverified', '代码已保留，未经运行验证'],
    ['partial', 'unverified', '生成未完成，部分源码已保留'],
    ['complete', 'failed', '验证失败，代码已保留'],
    ['partial', 'failed', '验证失败，代码已保留'],
  ])(
    'prioritizes verification failure for %s generation / %s verification',
    (generation_status, verification_status, title) => {
      const candidate = {
        ...run,
        result: { execution: 'source-candidate', generation_status, verification_status },
      }
      expect(sourceDeliveryState(candidate).title).toBe(title)
      expect(runNextAction(candidate)).toBe(title + '；源码可下载')
    },
  )

  it('keeps negative evidence and deduplicates pending steps across reports', () => {
    const source = sourceDeliveryState(
      run,
      { generation_status: 'complete', verification_status: 'passed', pending_steps: ['test'] },
      {
        execution: 'source-candidate',
        generation_status: 'partial',
        verification_status: 'failed',
        pending_steps: ['test', 'build'],
      },
    )
    expect(source.partial).toBe(true)
    expect(source.failed).toBe(true)
    expect(source.title).toBe('验证失败，代码已保留')
    expect(source.pendingSteps).toEqual(['test', 'build'])
  })

  it('does not turn completed source verification events into green acceptance', () => {
    const events = [{ id: 1, kind: 'stage', data: { name: 'verify', phase: 'completed' } }]
    expect(milestoneStatus(4, run, events)).toBe('pending')
    expect(milestoneStatus(4, { ...run, result: { verification_status: 'failed' } }, events)).toBe(
      'failed',
    )
    expect(milestoneStatus(4, { ...run, status: 'READY' }, events)).toBe('done')
    expect(milestoneStatus(3, { ...run, result: { generation_status: 'partial' } }, events)).toBe(
      'failed',
    )
  })
})
````
