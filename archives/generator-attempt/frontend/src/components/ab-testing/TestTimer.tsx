interface TestTimerProps {
  elapsed: number
  remaining: number
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  }
  return `${secs}s`
}

export function TestTimer({ elapsed, remaining }: TestTimerProps) {
  const isTimeout = remaining <= 0

  return (
    <div className="panel">
      <h3 className="font-bold mb-4">Test Duration</h3>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span style={{ color: 'var(--text-subtle)' }}>Elapsed Time</span>
          <span className="font-mono font-bold text-lg">{formatDuration(elapsed)}</span>
        </div>

        <div className="flex justify-between items-center">
          <span style={{ color: 'var(--text-subtle)' }}>Remaining</span>
          <span
            className="font-mono font-bold text-lg"
            style={{ color: isTimeout ? 'var(--error)' : 'var(--text-main)' }}
          >
            {isTimeout ? 'Timeout' : formatDuration(remaining)}
          </span>
        </div>

        {/* Progress bar showing test progress */}
        <div
          className="w-full rounded-full h-2 overflow-hidden"
          style={{ backgroundColor: 'rgba(0,0,0,0.1)' }}
        >
          <div
            className="h-full transition-all duration-1000"
            style={{
              width: `${Math.min(100, (elapsed / (elapsed + remaining)) * 100)}%`,
              backgroundColor: isTimeout ? 'var(--error)' : 'var(--run)',
            }}
          />
        </div>

        <p className="text-xs" style={{ color: 'var(--text-subtle)' }}>
          Auto-terminates after 72 hours if no significant winner
        </p>
      </div>
    </div>
  )
}
