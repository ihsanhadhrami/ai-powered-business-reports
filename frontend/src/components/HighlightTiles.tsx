interface HighlightTilesProps {
  kpis: Record<string, number> | null
  insights: string | null
}

export function HighlightTiles({ kpis, insights }: HighlightTilesProps) {
  const revenue = kpis?.total_revenue
  const growth = kpis?.revenue_growth

  return (
    <section className="mx-auto max-w-6xl px-6 py-16 grid md:grid-cols-2 gap-6">
      <div className="relative overflow-hidden rounded-2xl bg-violet p-10 diagonal-stripes">
        <div className="relative text-sm font-semibold text-ink/70 mb-3">Total Revenue</div>
        <div className="relative text-4xl md:text-5xl font-black">
          {revenue != null
            ? `$${revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
            : '—'}
        </div>
        {growth != null && (
          <div className="relative mt-3 text-sm font-semibold">
            {growth >= 0 ? '▲' : '▼'} {Math.abs(growth).toFixed(1)}% vs. previous period
          </div>
        )}
      </div>
      <div className="relative overflow-hidden rounded-2xl bg-[#eaf7ee] p-10 diagonal-stripes">
        <div className="relative text-sm font-semibold text-ink/70 mb-3">AI Insight</div>
        <p className="relative text-lg md:text-xl font-bold leading-snug line-clamp-5">
          {insights ?? 'Generate a report to see AI-written insights here.'}
        </p>
      </div>
    </section>
  )
}
