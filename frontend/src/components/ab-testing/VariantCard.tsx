import type { VariantMetrics } from '../../types/abtest'

interface VariantCardProps {
  variant: VariantMetrics
  isWinning: boolean
  isLeader: boolean
  thumbnailUrl?: string
}

const styleLabels: Record<string, string> = {
  face_focus: 'Face Focus',
  face_focused: 'Face Focus',
  product_demo: 'Product Demo',
  product_focused: 'Product Focused',
  viral: 'Viral',
  text_heavy: 'Text Heavy',
}

export function VariantCard({ variant, isWinning, isLeader, thumbnailUrl }: VariantCardProps) {
  const styleLabel = styleLabels[variant.style] || variant.style.replace(/_/g, ' ')

  return (
    <div
      className={`panel overflow-hidden ${isWinning ? 'thumbnail-card-active' : ''}`}
      style={{
        borderColor: isWinning ? 'var(--ok)' : isLeader ? 'var(--run)' : undefined,
        boxShadow: isWinning ? '0 0 0 3px rgba(32, 116, 91, 0.2)' : undefined,
      }}
    >
      {/* Badge */}
      {(isWinning || isLeader) && (
        <div
          className="absolute top-3 right-3 px-3 py-1 rounded-full text-sm font-bold text-white"
          style={{ backgroundColor: isWinning ? 'var(--ok)' : 'var(--run)', zIndex: 10 }}
        >
          {isWinning ? '🏆 WINNER' : '👑 LEADING'}
        </div>
      )}

      {/* Thumbnail Image */}
      <div className="thumbnail-image-container" style={{ margin: '-16px -16px 16px -16px' }}>
        {thumbnailUrl ? (
          <img src={thumbnailUrl} alt={styleLabel} className="thumbnail-image" loading="lazy" />
        ) : (
          <div
            className="flex items-center justify-center"
            style={{
              width: '100%',
              height: '100%',
              backgroundColor: 'rgba(0,0,0,0.05)',
              color: 'var(--text-subtle)',
            }}
          >
            No Preview
          </div>
        )}
        <span className="thumbnail-style-label">{styleLabel}</span>
      </div>

      {/* Stats */}
      <div>
        <div className="flex justify-between items-end mb-3">
          <span className="text-3xl font-bold" style={{ color: 'var(--text-main)' }}>
            {(variant.ctr * 100).toFixed(1)}%
          </span>
          <span className="text-sm mb-1" style={{ color: 'var(--text-subtle)' }}>
            CTR
          </span>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-subtle)' }}>Impressions</span>
            <span className="font-medium">{variant.impressions.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-subtle)' }}>Clicks</span>
            <span className="font-medium">{variant.clicks.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span style={{ color: 'var(--text-subtle)' }}>Avg View</span>
            <span className="font-medium">{variant.avg_view_duration}s</span>
          </div>
        </div>
      </div>
    </div>
  )
}
