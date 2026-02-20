export function ErrorFallback({ error, resetErrorBoundary }: { error: any; resetErrorBoundary: () => void }) {
    return (
        <section className="dashboard-grid">
            <div className="panel" style={{ gridColumn: 'span 12', textAlign: 'center', padding: '40px 20px' }}>
                <h2 style={{ color: 'var(--error)' }}>Something went wrong!</h2>
                <p style={{ marginTop: '12px', color: 'var(--text-subtle)' }}>
                    {error?.message || 'An unexpected error occurred in the UI.'}
                </p>
                <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
                    <button onClick={resetErrorBoundary}>Try Again</button>
                    <button
                        className="button-secondary"
                        onClick={() => {
                            resetErrorBoundary()
                            window.location.href = '/'
                        }}
                    >
                        Go to Dashboard
                    </button>
                </div>
            </div>
        </section>
    )
}
