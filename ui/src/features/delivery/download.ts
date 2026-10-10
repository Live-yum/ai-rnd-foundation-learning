import { check, headers } from '../../api'

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
