import { useEffect, useState } from 'react'
import type { VariantMetrics } from '../../types/abtest'

interface WinnerModalProps {
  winnerId: string
  variants: VariantMetrics[]
  onClose?: () => void
}

const styleLabels: Record<string, string> = {
  face_focus: 'Face Focus',
  face_focused: 'Face Focus',
  product_demo: 'Product Demo',
  product_focused: 'Product Focused',
  viral: 'Viral',
  text_heavy: 'Text Heavy',
}

export function WinnerModal({ winnerId, variants, onClose }: WinnerModalProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Trigger animation
    const timer = setTimeout(() => setIsVisible(true), 100)
    return () => clearTimeout(timer)
  }, [])

  const winner = variants.find((v) => v.thumbnail_id === winnerId)
  if (!winner) return null

  const styleLabel = styleLabels[winner.style] || winner.style.replace(/_/g, ' ')

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50"
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(5px)',
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 0.3s ease',
      }}
    >
      <div
        className="panel max-w-md w-full mx-4 text-center"
        style={{
          transform: isVisible ? 'scale(1)' : 'scale(0.9)',
          transition: 'transform 0.3s ease',
          borderColor: 'var(--ok)',
          boxShadow: '0 0 30px rgba(32, 116, 91, 0.3)',
        }}
      >
        {/* Celebration emoji */}
        <div className="text-6xl mb-4">🎉</div>

        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--ok)' }}>
          Winner Declared!
        </h2>

        <p className="mb-6" style={{ color: 'var(--text-subtle)' }}>
          The A/B test has determined the best performing thumbnail.
        </p>

        <div
          className="p-4 rounded-lg mb-6"
          style={{ backgroundColor: 'rgba(32, 116, 91, 0.08)' }}
        >
          <div className="text-sm mb-1" style={{ color: 'var(--text-subtle)' }}>
            Winning Variant
          </div>
          <div className="text-xl font-bold mb-2">{styleLabel}</div>
          <div className="text-3xl font-bold" style={{ color: 'var(--ok)' }}>
            {(winner.ctr * 100).toFixed(1)}% CTR
          </div>
          <div className="text-sm mt-1" style={{ color: 'var(--text-subtle)' }}>
            {winner.clicks.toLocaleString()} clicks / {winner.impressions.toLocaleString()} impressions
          </div>
        </div>

        <button onClick={onClose} className="w-full">
          View Results
        </button>
      </div>
    </div>
  )
}
