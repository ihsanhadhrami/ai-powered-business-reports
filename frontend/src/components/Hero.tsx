import type { DataInfoResponse } from '../api/client'
import { WaveBars } from './WaveBars'

interface HeroProps {
  dataInfo: DataInfoResponse | null
  onGenerate: () => void
  generating: boolean
}

export function Hero({ dataInfo, onGenerate, generating }: HeroProps) {
  return (
    <section className="relative overflow-hidden bg-hero-gradient pt-20">
      <div className="mx-auto max-w-4xl px-6 text-center">
        <h1 className="text-5xl md:text-7xl leading-[0.95] mb-6">
          Your business,
          <br />
          measured everywhere it matters.
        </h1>
        <p className="text-lg md:text-xl text-blue font-medium max-w-2xl mx-auto mb-10">
          Automated KPI tracking, AI-generated insights, and one-click email reports — all from
          your data.
        </p>
        <div className="inline-flex flex-col sm:flex-row items-stretch sm:items-center gap-2 bg-white rounded-3xl sm:rounded-full shadow-xl shadow-black/5 p-2 mb-2">
          <div className="px-5 py-2 text-left">
            <div className="text-xs text-ink-soft font-medium">Data source</div>
            <div className="text-sm font-semibold">
              {dataInfo
                ? `${dataInfo.rows} rows · ${dataInfo.date_min} → ${dataInfo.date_max}`
                : 'Loading current data…'}
            </div>
          </div>
          <button
            onClick={onGenerate}
            disabled={generating}
            className="pill pill-violet disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generating ? 'Generating…' : 'Generate Report'}
          </button>
        </div>
      </div>
      <WaveBars variant="light" className="w-full h-24 md:h-32 mt-10 block" />
    </section>
  )
}
