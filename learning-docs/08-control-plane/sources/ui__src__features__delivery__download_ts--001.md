# ui/src/features/delivery/download.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/features/delivery/download.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L17。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`498`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/features/delivery/download.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "22663fe842bfa1afe2f96ca31f8865166828396c3f5533995f929bf60a91d1b9"} -->
````typescript
// ui/src/features/delivery/download.ts
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
````
