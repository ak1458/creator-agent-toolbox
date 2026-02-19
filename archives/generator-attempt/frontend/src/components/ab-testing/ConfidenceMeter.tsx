interface ConfidenceMeterProps {
  confidence: number // 0.0 to 1.0
  minConfidence?: number // default 0.95
}

export function ConfidenceMeter({ confidence, minConfidence = 0.95 }: ConfidenceMeterProps) {
  const percentage = Math.round(confidence * 100)
  const isSignificant = confidence >= minConfidence

  // Color gradient based on confidence
  const getColor = () => {
    if (confidence >= 0.95) return '#20745b' // --ok
    if (confidence >= 0.9) return '#2f5ca8' // --run
    if (confidence >= 0.8) return '#b78717' // --warn
    return '#4f5e63' // --text-subtle
  }

  return (
    <div className="panel">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-bold">Statistical Confidence</h3>
        <span
          className="text-2xl font-bold"
          style={{ color: isSignificant ? 'var(--ok)' : 'var(--text-subtle)' }}
        >
          {percentage}%
        </span>
      </div>

      {/* Progress bar */}
      <div
        className="w-full rounded-full h-4 overflow-hidden"
        style={{ backgroundColor: 'rgba(0,0,0,0.1)' }}
      >
        <div
          className="h-full transition-all duration-1000"
          style={{ width: `${percentage}%`, backgroundColor: getColor() }}
        />
      </div>

      {/* Markers */}
      <div className="relative mt-1 h-5 text-xs" style={{ color: 'var(--text-subtle)' }}>
        <span className="absolute left-0">0%</span>
        <span
          className="absolute font-semibold"
          style={{ left: '95%', transform: 'translateX(-50%)', color: 'var(--error)' }}
        >
          95% (Target)
        </span>
      </div>

      {/* Status message */}
      <div
        className="mt-4 p-3 rounded-lg border-l-4"
        style={{
          backgroundColor: isSignificant ? 'rgba(32, 116, 91, 0.08)' : 'rgba(47, 92, 168, 0.08)',
          borderLeftColor: isSignificant ? 'var(--ok)' : 'var(--run)',
        }}
      >
        {isSignificant ? (
          <p className="font-medium" style={{ color: 'var(--ok)' }}>
            ✓ Statistical significance reached! Ready to declare winner.
          </p>
        ) : (
          <p style={{ color: 'var(--text-subtle)' }}>
            Collecting more data... Need {(minConfidence * 100).toFixed(0)}% confidence to auto-declare
            winner.
          </p>
        )}
      </div>
    </div>
  )
}
