import { Link } from 'react-router-dom'
import type { WorkflowSummary } from '../types/workflows'

interface WorkflowCardProps {
  workflow: WorkflowSummary
}

function toLocalTime(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleString()
}

function statusDisplay(status: string): { className: string; label: string; isPulsing?: boolean } {
  switch (status) {
    case 'completed':
      return { className: 'status-pill status-done', label: 'Ready to Publish' }
    case 'awaiting_approval':
      return { className: 'status-pill status-pending', label: 'Scripts Ready' }
    case 'awaiting_thumbnail_selection':
      return { className: 'status-pill status-urgent', label: 'Select Thumbnail' }
    case 'ab_testing':
      return { className: 'status-pill status-running', label: 'A/B Testing', isPulsing: true }
    case 'running':
      return { className: 'status-pill status-running', label: 'Processing' }
    default:
      return { className: 'status-pill status-running', label: status }
  }
}

function getActionText(status: string): string {
  switch (status) {
    case 'completed':
      return 'View'
    case 'awaiting_approval':
    case 'awaiting_thumbnail_selection':
      return 'Review'
    case 'ab_testing':
      return 'Monitor'
    default:
      return 'View'
  }
}

export function WorkflowCard({ workflow }: WorkflowCardProps) {
  const statusInfo = statusDisplay(workflow.status)
  const actionText = getActionText(workflow.status)

  return (
    <article className="panel workflow-card">
      <header>
        <h3>{workflow.topic}</h3>
        <span className={statusInfo.className}>{statusInfo.label}</span>
      </header>

      <dl>
        <div>
          <dt>ID</dt>
          <dd>{workflow.workflow_id}</dd>
        </div>
        <div>
          <dt>Step</dt>
          <dd>{workflow.current_step}</dd>
        </div>
        <div>
          <dt>Updated</dt>
          <dd>{toLocalTime(workflow.updated_ts)}</dd>
        </div>
      </dl>

      <Link
        className="button-link"
        to={
          workflow.status === 'ab_testing'
            ? `/workflows/${workflow.workflow_id}/ab-test`
            : `/workflows/${workflow.workflow_id}`
        }
      >
        {actionText}
      </Link>
    </article>
  )
}
