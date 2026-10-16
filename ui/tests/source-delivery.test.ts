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

  it('distinguishes approved runtime partial scope from partial source generation', () => {
    const partial = {
      ...run,
      result: { validation_level: 'runtime', delivery_kind: 'partial', production_ready: false },
    }
    expect(sourceDeliveryState(partial)).toMatchObject({
      sourceOnly: false,
      runtimePartial: true,
      partial: false,
    })
    expect(runNextAction(partial)).toBe(
      '部分成果已通过运行验收，完整需求仍未完成；查看验收证据与交付包',
    )
    expect(
      milestoneStatus(4, partial, [
        { id: 1, kind: 'stage', data: { name: 'extension_verify', phase: 'completed' } },
      ]),
    ).toBe('done')
    expect(sourceDeliveryState(run, partial.result).runtimePartial).toBe(true)
  })

  it.each([
    { execution: 'source-candidate' },
    { validation_level: 'source' },
    { runtime_verified: false },
    { verification_status: 'failed' as const },
  ])('preserves explicit source evidence over a conflicting runtime receipt: %j', (source) => {
    expect(
      sourceDeliveryState(run, { validation_level: 'runtime', delivery_kind: 'partial' }, source),
    ).toMatchObject({ sourceOnly: true, runtimePartial: false })
  })

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
