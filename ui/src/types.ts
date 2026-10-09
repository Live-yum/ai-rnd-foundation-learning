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
