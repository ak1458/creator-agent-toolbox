export function ReviewSkeleton() {
    return (
        <div className="dashboard-grid">
            <div className="panel" style={{ gridColumn: 'span 12', padding: '30px 20px', textAlign: 'center' }}>
                <h2 style={{ marginBottom: '8px' }} className="animate-pulse">
                    AI is analyzing trends...
                </h2>
                <p style={{ color: 'var(--text-subtle)', marginBottom: '24px' }}>
                    Generating creative variations based on viral data.
                </p>

                <div className="script-grid">
                    {Array.from({ length: 3 }).map((_, i) => (
                        <div
                            key={i}
                            className="panel skeleton"
                            style={{ padding: '20px', height: '140px', marginBottom: '10px' }}
                        ></div>
                    ))}
                </div>
            </div>
        </div>
    )
}
