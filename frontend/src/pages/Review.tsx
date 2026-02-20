import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { approveWorkflow, getWorkflow, selectThumbnail } from '../api/workflows'
import { ScriptVariant } from '../components/ScriptVariant'
import { ThumbnailVariant } from '../components/ThumbnailVariant'
import { ReviewSkeleton } from '../components/ReviewSkeleton'
import { ThumbnailSkeleton } from '../components/ThumbnailSkeleton'
import { toast } from 'react-hot-toast'

export function Review() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedScriptId, setSelectedScriptId] = useState<string | null>(null)
  const [selectedThumbnailId, setSelectedThumbnailId] = useState<string | null>(null)

  const workflowQuery = useQuery({
    queryKey: ['workflow', id],
    queryFn: () => getWorkflow(id as string),
    enabled: Boolean(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      // Poll more frequently when generating thumbnails or waiting for approval
      if (status === 'awaiting_approval' || status === 'running' || status === 'awaiting_thumbnail_selection') {
        return 2000
      }
      return false
    },
  })

  const workflow = workflowQuery.data

  // Determine which stage we're in
  const isAwaitingScriptApproval = workflow?.status === 'awaiting_approval'
  const isAwaitingThumbnailSelection = workflow?.status === 'awaiting_thumbnail_selection'
  const isABTesting = workflow?.status === 'ab_testing'

  // Redirect to AB test monitor if in AB testing phase
  useEffect(() => {
    if (isABTesting && id) {
      navigate(`/workflows/${id}/ab-test`)
    }
  }, [isABTesting, id, navigate])

  // Initialize selected script from workflow data
  useEffect(() => {
    if (!workflow?.scripts?.length) {
      setSelectedScriptId(null)
      return
    }

    const selected = workflow.selected_script_id ?? workflow.scripts[0].id
    setSelectedScriptId((previous) => previous ?? selected)
  }, [workflow?.scripts, workflow?.selected_script_id])

  // Initialize selected thumbnail from workflow data
  useEffect(() => {
    if (!workflow?.thumbnails?.length) {
      setSelectedThumbnailId(null)
      return
    }

    const selected = workflow.selected_thumbnail_id ?? workflow.thumbnails[0].id
    setSelectedThumbnailId((previous) => previous ?? selected)
  }, [workflow?.thumbnails, workflow?.selected_thumbnail_id])

  const approveMutation = useMutation({
    mutationFn: async () => {
      if (!id || !selectedScriptId) {
        throw new Error('Select a script before approving')
      }
      return approveWorkflow(id, {
        action: 'approve',
        selected_script_id: selectedScriptId,
      })
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['workflow', id] }),
        queryClient.invalidateQueries({ queryKey: ['workflows'] }),
      ])
      toast.success('Script approved successfully!')
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Error approving script')
    }
  })

  const rejectMutation = useMutation({
    mutationFn: async () => {
      if (!id) {
        throw new Error('Missing workflow id')
      }
      return approveWorkflow(id, {
        action: 'reject',
      })
    },
    onSuccess: async (data) => {
      setSelectedScriptId(data.scripts[0]?.id ?? null)
      setSelectedThumbnailId(null)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['workflow', id] }),
        queryClient.invalidateQueries({ queryKey: ['workflows'] }),
      ])
      toast.success('Scripts rejected, regenerating...')
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Error rejecting scripts')
    }
  })

  const selectThumbnailMutation = useMutation({
    mutationFn: async () => {
      if (!id || !selectedThumbnailId) {
        throw new Error('Select a thumbnail before finalizing')
      }
      return selectThumbnail(id, {
        selected_thumbnail_id: selectedThumbnailId,
      })
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['workflow', id] }),
        queryClient.invalidateQueries({ queryKey: ['workflows'] }),
      ])
      toast.success('Thumbnail selected! Starting A/B test...')
      // Navigate to AB test monitor after thumbnail selection
      navigate(`/workflows/${id}/ab-test`)
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Error selecting thumbnail')
    }
  })

  const activeError = useMemo(() => {
    if (approveMutation.error instanceof Error) {
      return approveMutation.error.message
    }
    if (rejectMutation.error instanceof Error) {
      return rejectMutation.error.message
    }
    if (selectThumbnailMutation.error instanceof Error) {
      return selectThumbnailMutation.error.message
    }
    return null
  }, [approveMutation.error, rejectMutation.error, selectThumbnailMutation.error])

  if (!id) {
    return (
      <section className="panel">
        <p className="error-text">Missing workflow id.</p>
        <Link to="/">Back to dashboard</Link>
      </section>
    )
  }

  if (workflowQuery.isLoading) {
    return (
      <section className="panel">
        <p>Loading workflow...</p>
      </section>
    )
  }

  if (workflowQuery.error || !workflow) {
    return (
      <section className="panel">
        <p className="error-text">Failed to load workflow.</p>
        <Link to="/">Back to dashboard</Link>
      </section>
    )
  }

  const isRunning = workflow.status === 'running'
  const isCompleted = workflow.status === 'completed'

  // Stage 1: Script Selection
  const isScriptStage = isAwaitingScriptApproval

  // Stage 2: Thumbnail Selection (or running after script approval)
  const isThumbnailStage = isAwaitingThumbnailSelection || (isRunning && workflow.selected_script_id && !workflow.thumbnails?.length)

  // Loading state: generating thumbnails
  const isGeneratingThumbnails = isRunning && workflow.selected_script_id && !workflow.thumbnails?.length

  const scriptActionDisabled =
    !isAwaitingScriptApproval ||
    approveMutation.isPending ||
    rejectMutation.isPending ||
    !selectedScriptId

  const thumbnailActionDisabled =
    !isAwaitingThumbnailSelection ||
    selectThumbnailMutation.isPending ||
    !selectedThumbnailId

  return (
    <section className="review-layout">
      <section className="panel review-summary">
        <h2>Workflow {workflow.workflow_id}</h2>
        <p>
          Status: <strong>{workflow.status}</strong>
        </p>
        <p>
          Step: <strong>{workflow.current_step}</strong>
        </p>
        {workflow.requires_action ? <p>Action required: {workflow.requires_action}</p> : null}
        <Link className="button-link ghost" to="/">
          Back to dashboard
        </Link>
      </section>

      {/* Stage 1: Script Selection */}
      {workflow.status === 'generating_scripts' && <ReviewSkeleton />}
      {(isScriptStage || workflow.scripts.length > 0) && workflow.status !== 'generating_scripts' && (
        <section className="panel">
          <h2>Script Variants</h2>
          {!workflow.scripts.length ? <p>No script variants available yet.</p> : null}
          <div className="script-grid">
            {workflow.scripts.map((script) => (
              <ScriptVariant
                key={script.id}
                variant={script}
                checked={selectedScriptId === script.id}
                disabled={!isAwaitingScriptApproval}
                onSelect={setSelectedScriptId}
              />
            ))}
          </div>

          {isAwaitingScriptApproval && (
            <div className="action-row">
              <button
                type="button"
                onClick={() => approveMutation.mutate()}
                disabled={scriptActionDisabled}
              >
                {approveMutation.isPending ? 'Approving...' : 'Approve Script'}
              </button>
              <button
                type="button"
                className="button-secondary"
                onClick={() => rejectMutation.mutate()}
                disabled={!isAwaitingScriptApproval || rejectMutation.isPending}
              >
                {rejectMutation.isPending ? 'Regenerating...' : 'Reject All'}
              </button>
            </div>
          )}
          {isCompleted && workflow.selected_script_id && (
            <p className="success-text">Script approved and finalized.</p>
          )}
        </section>
      )}

      {/* Loading: Generating Thumbnails */}
      {isGeneratingThumbnails && <ThumbnailSkeleton />}

      {/* Stage 2: Thumbnail Selection */}
      {(isThumbnailStage || workflow.thumbnails.length > 0) && !isGeneratingThumbnails && (
        <section className="panel">
          <h2>Thumbnail Variants</h2>
          {!workflow.thumbnails.length ? (
            <p>No thumbnail variants available yet.</p>
          ) : (
            <>
              <p className="thumbnail-help-text">
                Select the thumbnail that best represents your content.
              </p>
              <div className="thumbnail-grid">
                {workflow.thumbnails.map((thumbnail) => (
                  <ThumbnailVariant
                    key={thumbnail.id}
                    variant={thumbnail}
                    checked={selectedThumbnailId === thumbnail.id}
                    disabled={!isAwaitingThumbnailSelection}
                    onSelect={setSelectedThumbnailId}
                  />
                ))}
              </div>
            </>
          )}

          {isAwaitingThumbnailSelection && (
            <div className="action-row">
              <button
                type="button"
                onClick={() => selectThumbnailMutation.mutate()}
                disabled={thumbnailActionDisabled}
              >
                {selectThumbnailMutation.isPending ? 'Finalizing...' : 'Finalize Content'}
              </button>
            </div>
          )}
          {isCompleted && workflow.selected_thumbnail_id && (
            <p className="success-text">Thumbnail selected and content finalized.</p>
          )}
        </section>
      )}

      {/* Completion Summary */}
      {isCompleted && (
        <section className="panel completion-summary">
          <h2>Content Ready to Publish</h2>
          <div className="completion-details">
            {workflow.selected_script_id && (
              <div className="completion-item">
                <strong>Selected Script:</strong>{' '}
                {workflow.scripts.find(s => s.id === workflow.selected_script_id)?.hook || workflow.selected_script_id}
              </div>
            )}
            {workflow.selected_thumbnail_id && workflow.thumbnails.find(t => t.id === workflow.selected_thumbnail_id)?.image_url && (
              <div className="completion-item">
                <strong>Selected Thumbnail:</strong>
                <img
                  src={workflow.thumbnails.find(t => t.id === workflow.selected_thumbnail_id)?.image_url}
                  alt="Selected thumbnail"
                  className="completion-thumbnail"
                />
              </div>
            )}
          </div>
        </section>
      )}

      {activeError ? <p className="error-text">{activeError}</p> : null}
    </section>
  )
}
