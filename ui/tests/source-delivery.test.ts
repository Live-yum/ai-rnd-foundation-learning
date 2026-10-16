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
