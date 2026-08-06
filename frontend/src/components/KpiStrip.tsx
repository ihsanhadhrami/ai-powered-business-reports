import { formatLabel, formatValue } from '../lib/format'

interface KpiStripProps {
  kpis: Record<string, number> | null
}

function dotColorFor(key: string, value: number): string {
  if (!key.includes('growth')) return 'bg-blue'
  if (value > 0) return 'bg-emerald-400'
  if (value < 0) return 'bg-danger'
  return 'bg-ink-soft'
}

export function KpiStrip({ kpis }: KpiStripProps) {
  if (!kpis) return null
  const entries = Object.entries(kpis)
  if (entries.length === 0) return null

  return (
    <div className="bg-[#f1ecfb]/60 border-y border-black/5">
      <div className="mx-auto max-w-6xl px-6 py-6 flex flex-wrap gap-x-10 gap-y-4 justify-center">
        {entries.map(([key, value]) => (
          <div key={key} className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${dotColorFor(key, value)}`} />
            <div>
              <div className="text-xs text-ink-soft">{formatLabel(key)}</div>
              <div className="text-sm font-bold">{formatValue(key, value)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
