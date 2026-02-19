export type WorkflowAction = 'approve' | 'reject'

export interface ScriptVariant {
  id: string
  hook: string
  body: string
  cta: string
  tone?: string
  predicted_retention?: number
}

export interface ThumbnailVariant {
  id: string
  style: string
  prompt: string
  image_url: string
  seed: number
}

export interface WorkflowSummary {
  workflow_id: string
  topic: string
  status: string
  current_step: string
  created_ts: number
  updated_ts: number
}

export interface WorkflowDetail {
  workflow_id: string
  status: string
  current_step: string
  requires_action: string | null
  scripts: ScriptVariant[]
  selected_script_id: string | null
  thumbnails: ThumbnailVariant[]
  selected_thumbnail_id: string | null
  token_usage: Record<string, number>
}

export interface StartWorkflowPayload {
  topic: string
  platforms: string[]
  user_id?: string
  brand_voice?: string
}

export interface ApproveWorkflowPayload {
  selected_script_id?: string
  action: WorkflowAction
}

export interface SelectThumbnailPayload {
  selected_thumbnail_id: string
}
