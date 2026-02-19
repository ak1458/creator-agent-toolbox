import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import type { VariantMetrics } from '../../types/abtest'

interface CTRChartProps {
  variants: VariantMetrics[]
}

const COLORS = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

export function CTRChart({ variants }: CTRChartProps) {
  // Transform data for Recharts - show CTR as percentage
  const data = variants.map((v) => ({
    name: v.style.replace(/_/g, ' '),
    ctr: Number((v.ctr * 100).toFixed(2)), // Convert to percentage
    impressions: v.impressions,
    clicks: v.clicks,
    thumbnail_id: v.thumbnail_id,
  }))

  return (
    <div className="panel">
      <h3 className="text-lg font-bold mb-4">Click-Through Rate Performance</h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} />
            <YAxis unit="%" domain={[0, 'auto']} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value) => [`${value}%`, 'CTR']}
              contentStyle={{
                backgroundColor: 'var(--panel-bg)',
                border: '1px solid var(--panel-border)',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Bar dataKey="ctr" name="CTR %" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${entry.thumbnail_id}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4 text-center text-sm" style={{ color: 'var(--text-subtle)' }}>
        {variants.map((v, i) => (
          <div key={v.thumbnail_id} className="p-2" style={{ backgroundColor: 'rgba(0,0,0,0.03)', borderRadius: '8px' }}>
            <span
              className="inline-block w-3 h-3 rounded-full mr-2"
              style={{ backgroundColor: COLORS[i % COLORS.length] }}
            />
            <strong>{v.clicks.toLocaleString()}</strong> clicks /{' '}
            <strong>{v.impressions.toLocaleString()}</strong> views
          </div>
        ))}
      </div>
    </div>
  )
}
