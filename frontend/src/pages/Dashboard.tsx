import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../api/client'
import { listWorkflows, startWorkflow } from '../api/workflows'
import { WorkflowCard } from '../components/WorkflowCard'
import { useWorkflowStore } from '../stores/workflowStore'

function topicPlaceholder() {
  return 'e.g. iPhone Battery Tips'
}

export function Dashboard() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setSelectedWorkflowId = useWorkflowStore((state) => state.setSelectedWorkflowId)
  const [topic, setTopic] = useState('')
  const [createError, setCreateError] = useState<string | null>(null)

  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await apiClient.get<{ status: string }>('/api/v1/health')
      return response.data
    },
    refetchInterval: 10000,
  })

  const workflowsQuery = useQuery({
    queryKey: ['workflows'],
    queryFn: listWorkflows,
    refetchInterval: 5000,
  })

  const createWorkflowMutation = useMutation({
    mutationFn: (workflowTopic: string) =>
      startWorkflow({
        topic: workflowTopic,
        platforms: ['youtube'],
      }),
    onSuccess: async (workflow) => {
      setCreateError(null)
      setTopic('')
      setSelectedWorkflowId(workflow.workflow_id)
      await queryClient.invalidateQueries({ queryKey: ['workflows'] })
      navigate(`/workflows/${workflow.workflow_id}`)
    },
    onError: (error) => {
      setCreateError(error instanceof Error ? error.message : 'Failed to start workflow')
    },
  })

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const normalized = topic.trim()
    if (!normalized) {
      setCreateError('Topic is required')
      return
    }
    createWorkflowMutation.mutate(normalized)
  }

  return (
    <section className="dashboard-grid">
      <section className="panel new-workflow-panel">
        <h2>New Workflow</h2>
        <p>Start a script workflow and route it to human approval.</p>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
            placeholder={topicPlaceholder()}
            maxLength={160}
          />
          <button type="submit" disabled={createWorkflowMutation.isPending}>
            {createWorkflowMutation.isPending ? 'Creating...' : 'Create Workflow'}
          </button>
        </form>
        {createError ? <p className="error-text">{createError}</p> : null}
      </section>

      <section className="panel health-panel">
        <h2>Backend Health</h2>
        {healthQuery.isLoading ? <p>Checking health...</p> : null}
        {healthQuery.error ? <p className="error-text">API not reachable</p> : null}
        {healthQuery.data ? <p>Status: {healthQuery.data.status}</p> : null}
      </section>

      <section className="workflow-list-section">
        <div className="section-head">
          <h2>Workflows</h2>
          <button
            type="button"
            onClick={() => workflowsQuery.refetch()}
            disabled={workflowsQuery.isFetching}
          >
            Refresh
          </button>
        </div>

        {workflowsQuery.isLoading ? <p>Loading workflows...</p> : null}
        {workflowsQuery.error ? <p className="error-text">Failed to load workflows</p> : null}

        <div className="workflow-grid">
          {workflowsQuery.data?.map((workflow) => (
            <WorkflowCard key={workflow.workflow_id} workflow={workflow} />
          ))}
        </div>
      </section>
    </section>
  )
}
