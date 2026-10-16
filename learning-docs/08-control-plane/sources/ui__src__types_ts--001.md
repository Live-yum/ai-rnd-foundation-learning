# ui/src/types.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 定义浏览器持有的项目、运行、消息与事件形状；TypeScript约束本地使用，不能替代服务端输入验证。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/types.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L85。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1942`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/types.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d0f8bc672b8e6aa6a0eedfd60a366abae5829510b5e7b471f25249d068d7a133"} -->
````typescript
// ui/src/types.ts
export type RecordData = Record<string, any>
export interface Project {
  id: string
  title: string
  created_at?: string
}
export interface Gate {
  gate_id: string
  version: number
  digest: string
  stage: string
  data: RecordData
  actions: string[]
  can_approve: boolean
  needs_model?: Record<string, boolean>
}
export interface SourceDeliveryEvidence {
  execution?: string
  generation_status?: 'complete' | 'partial'
  verification_status?: 'unverified' | 'failed' | 'passed'
  pending_steps?: string[]
  runtime_unavailable_reason?: string
  runtime_verified?: boolean
  production_ready?: boolean
  acceptance_passed?: boolean
  source_checks_passed?: boolean
  source_commit?: { commit?: string; status?: string; git_available?: boolean }
}
export interface Run {
  id: string
  project_id: string
  status: string
  template: string
  options?: RecordData
  auto_mode: boolean
  pending?: Gate | null
  result?: RecordData
  error?: string
  updated_at?: string
  created_at?: string
  [key: string]: any
}
export interface RunEvent {
  id: number
  kind: string
  data: RecordData
  created_at?: string
}
export interface ChatMessage {
  id?: string | number
  message_id?: string
  role: string
  content?: string
  text?: string
  stage?: string
  validation?: string
  transport?: string
  status?: string
  created_at?: string
  [key: string]: any
}
export interface CatalogEntry {
  template: string
  name: string
  backend: string
  frontends: string[]
  databases: string[]
  features: string[]
  coding_standard?: { path: string; sha256?: string; summary?: string; content?: string }
  [key: string]: any
}
export interface Selection {
  template: string
  backend: string
  frontend: string
  database: string
}
export interface ProjectDraft {
  id: string
  title: string
  requirement: string
}
export interface BatchReceipt {
  items: { project_id: string; title: string; run_id: string; status: 'QUEUED' }[]
}
````
