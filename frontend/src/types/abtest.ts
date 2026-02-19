import type { ScriptVariant, ThumbnailVariant } from './workflows'

export interface VariantMetrics {
  thumbnail_id: string
  style: 'FACE_FOCUSED' | 'PRODUCT_DEMO' | 'VIRAL' | 'TEXT_HEAVY' | string
  impressions: number
  clicks: number
  ctr: number // 0.085 = 8.5%
  avg_view_duration: number
  confidence: number
}

export interface ABTestStatus {
  workflow_id: string
  status: 'running' | 'completed' | 'timeout' | 'manual_override'
  is_running: boolean
  variants: VariantMetrics[]
  current_confidence: number
  total_impressions: number
  winner_id: string | null
  elapsed_time_seconds: number
  estimated_time_remaining: number
  checks_completed: number
  can_declare_early: boolean
}

export interface ABTestResults {
  winning_content: {
    script: ScriptVariant
    thumbnail: ThumbnailVariant
    combined_ctr: number
  }
  ab_test_summary: {
    duration_hours: number
    total_impressions: number
    confidence_reached: number
    was_manual_override: boolean
  }
}
