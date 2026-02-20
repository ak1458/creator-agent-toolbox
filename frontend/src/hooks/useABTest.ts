import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../api/client'
import type { ABTestStatus } from '../types/abtest'
import { toast } from 'react-hot-toast'

const POLL_INTERVAL = 5000 // 5 seconds for real-time feel

export const useABTest = (workflowId: string | undefined) => {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  // Main polling query
  const { data, isLoading, error } = useQuery<ABTestStatus>({
    queryKey: ['ab-test', workflowId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/workflows/${workflowId}/ab-status`)
      return response.data
    },
    refetchInterval: (query) => {
      // Stop polling if test is complete
      const status = query.state.data?.is_running
      return status ? POLL_INTERVAL : false
    },
    enabled: !!workflowId,
  })

  // Manual winner declaration
  const declareWinner = useMutation({
    mutationFn: async (thumbnailId: string) => {
      const response = await apiClient.post(
        `/api/v1/workflows/${workflowId}/declare-winner`,
        { thumbnail_id: thumbnailId },
      )
      return response.data
    },
    onSuccess: () => {
      // Invalidate and refetch immediately
      queryClient.invalidateQueries({ queryKey: ['ab-test', workflowId] })
      queryClient.invalidateQueries({ queryKey: ['workflow', workflowId] })
      toast.success('Winner declared manually!')
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Error declaring winner')
    }
  })

  // Stop test early
  const stopTest = useMutation({
    mutationFn: async (reason?: string) => {
      const response = await apiClient.post(
        `/api/v1/workflows/${workflowId}/stop-test`,
        { reason: reason || 'manual_stop' },
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ab-test', workflowId] })
      toast.success('Test stopped early. Winner selected based on best CTR.')
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Error stopping test')
    }
  })

  // Auto-redirect effect when complete
  useEffect(() => {
    if (data?.status === 'completed' && !data.is_running && workflowId) {
      // Trigger winner celebration or redirect after short delay
      const timer = setTimeout(() => {
        navigate(`/workflows/${workflowId}`)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [data, workflowId, navigate])

  return {
    data,
    isLoading,
    error,
    declareWinner,
    stopTest,
    isDeclaring: declareWinner.isPending,
    isStopping: stopTest.isPending,
  }
}
