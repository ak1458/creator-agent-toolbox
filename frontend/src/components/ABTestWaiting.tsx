export function ABTestWaiting({ impressions }: { impressions: number }) {
    return (
        <div className="panel" style={{ padding: '40px 20px', textAlign: 'center' }}>
            <h2 style={{ marginBottom: '8px' }} className="animate-pulse">
                Collecting viewer data...
            </h2>
            <p style={{ color: 'var(--text-subtle)', marginBottom: '24px' }}>
                The A/B test is live. We need more data to declare a statistically significant winner.
            </p>

            {/* Mini chart placeholder */}
            <div
                style={{
                    height: '100px',
                    maxWidth: '300px',
                    margin: '0 auto 24px',
                    borderBottom: '2px solid var(--line)',
                    borderLeft: '2px solid var(--line)',
                    position: 'relative'
                }}
            >
                <div
                    className="skeleton"
                    style={{
                        position: 'absolute',
                        bottom: '0',
                        left: '10%',
                        width: '20%',
                        height: '30%',
                        backgroundColor: 'var(--run)'
                    }}
                ></div>
                <div
                    className="skeleton"
                    style={{
                        position: 'absolute',
                        bottom: '0',
                        left: '40%',
                        width: '20%',
                        height: '60%',
                        backgroundColor: 'var(--run)'
                    }}
                ></div>
                <div
                    className="skeleton"
                    style={{
                        position: 'absolute',
                        bottom: '0',
                        left: '70%',
                        width: '20%',
                        height: '40%',
                        backgroundColor: 'var(--run)'
                    }}
                ></div>
            </div>

            <p style={{ fontWeight: 500 }}>
                {impressions} impressions so far
            </p>
        </div>
    )
}
