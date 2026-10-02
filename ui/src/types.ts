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
  [key: string]: any
}
