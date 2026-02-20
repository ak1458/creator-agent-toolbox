import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useABTest } from '../hooks/useABTest'
import { CTRChart } from '../components/ab-testing/CTRChart'
import { ConfidenceMeter } from '../components/ab-testing/ConfidenceMeter'
import { VariantCard } from '../components/ab-testing/VariantCard'
import { TestTimer } from '../components/ab-testing/TestTimer'
import { WinnerModal } from '../components/ab-testing/WinnerModal'
import { ABTestWaiting } from '../components/ABTestWaiting'
import { useWorkflow } from '../hooks/useWorkflow'

export function ABTestMonitor() {
  const { id } = useParams<{ id: string }>()
  const { data, isLoading, error, declareWinner, isDeclaring } = useABTest(id)
  const { data: workflowData } = useWorkflow(id)
  const [showWinnerModal, setShowWinnerModal] = useState(true)

  // Get thumbnail URLs from workflow data
  const thumbnailUrls =
    workflowData?.thumbnails?.reduce(
      (acc, t) => {
        acc[t.id] = t.image_url
        return acc
      },
      {} as Record<string, string>,
    ) || {}

  if (isLoading) {
    return (
      <section className="panel">
        <p>Loading A/B test data...</p>
      </section>
    )
  }

  if (error || !data) {
    return (
      <section className="panel">
        <p className="error-text">Failed to load A/B test data.</p>
        <Link to="/">Back to dashboard</Link>
      </section>
    )
  }

  const handleManualWinner = (thumbnailId: string) => {
    if (window.confirm('Are you sure you want to manually declare this variant as winner?')) {
      declareWinner.mutate(thumbnailId)
    }
  }

  const handleCloseWinnerModal = () => {
    setShowWinnerModal(false)
  }

  // Find leader (highest CTR)
  const leaderId =
    data.variants.length > 0
      ? data.variants.reduce((max, v) => (v.ctr > max.ctr ? v : max), data.variants[0]).thumbnail_id
      : null

  return (
    <section className="review-layout">
      {/* Winner Modal */}
      {data.winner_id && showWinnerModal && (
        <WinnerModal winnerId={data.winner_id} variants={data.variants} onClose={handleCloseWinnerModal} />
      )}

      {/* Header */}
      <section className="panel review-summary">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <h2>A/B Test Monitor</h2>
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              {data.is_running && (
                <span
                  className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                  style={{ backgroundColor: 'var(--ok)' }}
                />
              )}
              <span
                className="relative inline-flex rounded-full h-3 w-3"
                style={{ backgroundColor: data.is_running ? 'var(--ok)' : 'var(--text-subtle)' }}
              />
            </span>
            <span className="font-medium capitalize">{data.status.replace(/_/g, ' ')}</span>
          </div>
        </div>
        <p style={{ color: 'var(--text-subtle)', marginTop: '8px' }}>
          Testing {data.variants.length} thumbnail variants • {data.total_impressions.toLocaleString()} total
          impressions
        </p>
        <Link className="button-link ghost" to="/" style={{ marginTop: '12px' }}>
          Back to dashboard
        </Link>
      </section>

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Left: Charts */}
        <div className="workflow-list-section" style={{ gridColumn: 'span 8', minHeight: '256px', width: '100%', overflow: 'hidden' }}>
          {data.is_running && data.total_impressions < 50 ? (
            <ABTestWaiting impressions={data.total_impressions} />
          ) : (
            <>
              <CTRChart variants={data.variants} />
              <div style={{ marginTop: '16px' }}>
                <ConfidenceMeter confidence={data.current_confidence} />
              </div>
            </>
          )}
        </div>

        {/* Right: Stats & Controls */}
        <div style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <TestTimer elapsed={data.elapsed_time_seconds} remaining={data.estimated_time_remaining} />

          <section className="panel">
            <h3 className="font-bold mb-4">Manual Override</h3>
            <p className="text-sm mb-4" style={{ color: 'var(--text-subtle)' }}>
              Don't want to wait? Pick the winner based on your judgment.
            </p>
            <div className="space-y-2">
              {data.variants.map((variant) => (
                <button
                  key={variant.thumbnail_id}
                  type="button"
                  onClick={() => handleManualWinner(variant.thumbnail_id)}
                  disabled={isDeclaring || !data.is_running}
                  className="w-full p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                  style={{
                    borderColor: 'var(--panel-border)',
                    borderRadius: '8px',
                    backgroundColor: 'transparent',
                    cursor: data.is_running ? 'pointer' : 'not-allowed',
                  }}
                >
                  <div className="flex justify-between items-center w-full">
                    <span className="font-medium truncate" style={{ maxWidth: '70%' }}>
                      {variant.style.replace(/_/g, ' ').toLowerCase()}
                    </span>
                    <span className="font-bold" style={{ color: 'var(--run)' }}>
                      {(variant.ctr * 100).toFixed(1)}%
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </section>
        </div>
      </div>

      {/* Variant Thumbnails Grid */}
      <section className="panel">
        <h2 className="mb-4">Live Variant Performance</h2>
        <div
          className="thumbnail-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '16px',
          }}
        >
          {data.variants.map((variant) => (
            <VariantCard
              key={variant.thumbnail_id}
              variant={variant}
              isWinning={variant.thumbnail_id === data.winner_id}
              isLeader={!data.winner_id && variant.thumbnail_id === leaderId}
              thumbnailUrl={thumbnailUrls[variant.thumbnail_id]}
            />
          ))}
        </div>
      </section>
    </section>
  )
}
