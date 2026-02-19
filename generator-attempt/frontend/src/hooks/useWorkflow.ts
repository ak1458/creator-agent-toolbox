import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { WorkflowDetail } from '../types/workflows'

export const useWorkflow = (workflowId: string | undefined) => {
  return useQuery<WorkflowDetail>({
    queryKey: ['workflow', workflowId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/workflows/${workflowId}/status`)
      return response.data
    },
    enabled: !!workflowId,
    refetchInterval: 5000,
  })
}
