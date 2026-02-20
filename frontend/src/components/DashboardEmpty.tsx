export function DashboardEmpty() {
    return (
        <div className="panel" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '60px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ color: 'var(--run)', marginBottom: '16px' }}
            >
                <path d="M12 3a9 9 0 0 0 0 18 9 9 0 0 0 0-18Z" />
                <path d="M12 8v8" />
                <path d="M8 12h8" />
            </svg>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '8px' }}>Create Your First Viral Video</h2>
            <p style={{ color: 'var(--text-subtle)', maxWidth: '400px', marginBottom: '24px' }}>
                AI writes the script, generates thumbnails, and A/B tests automatically
            </p>
            {/* Reusing the same button visually, the actual action is handled by the form above */}
            <button
                onClick={() => document.getElementById('topic-input')?.focus()}
                style={{ padding: '12px 24px', fontSize: '1.1rem' }}
            >
                Start New Workflow
            </button>
        </div>
    )
}
