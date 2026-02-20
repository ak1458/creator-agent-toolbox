export function ThumbnailSkeleton() {
    return (
        <div className="panel" style={{ marginTop: '20px', textAlign: 'center', padding: '30px 20px' }}>
            <h2 style={{ marginBottom: '8px' }} className="animate-pulse">
                Designing visual variants...
            </h2>
            <p style={{ color: 'var(--text-subtle)', marginBottom: '24px' }}>
                Rendering high-converting thumbnails.
            </p>

            <div className="thumbnail-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                {Array.from({ length: 3 }).map((_, i) => (
                    <div
                        key={i}
                        className="skeleton"
                        style={{ width: '100%', aspectRatio: '16/9', borderRadius: '8px' }}
                    ></div>
                ))}
            </div>
        </div>
    )
}
