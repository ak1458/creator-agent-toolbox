import { apiClient } from './client'
import type {
  ApproveWorkflowPayload,
  SelectThumbnailPayload,
  StartWorkflowPayload,
  WorkflowDetail,
  WorkflowSummary,
} from '../types/workflows'

const WORKFLOWS_BASE = '/api/v1/workflows'

export async function listWorkflows(): Promise<WorkflowSummary[]> {
  const response = await apiClient.get<WorkflowSummary[]>(WORKFLOWS_BASE)
  return response.data
}

export async function getWorkflow(workflowId: string): Promise<WorkflowDetail> {
  const response = await apiClient.get<WorkflowDetail>(`${WORKFLOWS_BASE}/${workflowId}/status`)
  return response.data
}

export async function startWorkflow(payload: StartWorkflowPayload): Promise<WorkflowDetail> {
  const response = await apiClient.post<WorkflowDetail>(`${WORKFLOWS_BASE}/start`, payload)
  return response.data
}

export async function approveWorkflow(
  workflowId: string,
  payload: ApproveWorkflowPayload,
): Promise<WorkflowDetail> {
  const response = await apiClient.post<WorkflowDetail>(
    `${WORKFLOWS_BASE}/${workflowId}/approve`,
    payload,
  )
  return response.data
}

export async function selectThumbnail(
  workflowId: string,
  payload: SelectThumbnailPayload,
): Promise<WorkflowDetail> {
  const response = await apiClient.post<WorkflowDetail>(
    `${WORKFLOWS_BASE}/${workflowId}/select-thumbnail`,
    payload,
  )
  return response.data
}
