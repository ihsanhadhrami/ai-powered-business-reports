import { useState } from 'react'
import type { ReportPreviewResponse } from '../api/client'
import { formatLabel, formatValue } from '../lib/format'

interface ReportPreviewPanelProps {
  preview: ReportPreviewResponse | null
  loading: boolean
  onRegenerate: () => void
}

const SECTIONS = ['Overview', 'Email Preview'] as const
type Section = (typeof SECTIONS)[number]

export function ReportPreviewPanel({ preview, loading, onRegenerate }: ReportPreviewPanelProps) {
  const [tab, setTab] = useState<Section>('Overview')

  return (
    <section id="dashboard" className="mx-auto max-w-6xl px-6 py-16">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl">Report Preview</h2>
        <button
          onClick={onRegenerate}
          disabled={loading}
          className="pill pill-outline text-sm py-2 px-4 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Regenerating…' : 'Regenerate'}
        </button>
      </div>
      <div className="rounded-2xl border border-black/10 shadow-xl shadow-black/5 overflow-hidden bg-white">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-black/10 bg-[#f8fafc]">
          <span className="w-3 h-3 rounded-full bg-[#ff5f57]" />
          <span className="w-3 h-3 rounded-full bg-[#febc2e]" />
          <span className="w-3 h-3 rounded-full bg-[#28c840]" />
          <span className="ml-3 text-xs text-ink-soft truncate">
            {preview?.subject ?? 'No report generated yet'}
          </span>
        </div>
        <div className="flex flex-col md:flex-row">
          <aside className="md:w-44 shrink-0 border-b md:border-b-0 md:border-r border-black/10 p-4 flex md:block gap-1">
            {SECTIONS.map((section) => (
              <button
                key={section}
                onClick={() => setTab(section)}
                className={`text-left text-sm rounded-lg px-3 py-2 mb-1 font-medium ${
                  tab === section ? 'bg-black/5 text-ink' : 'text-ink-soft hover:bg-black/5'
                }`}
              >
                {section}
              </button>
            ))}
          </aside>
          <div className="flex-1 min-w-0">
            {!preview ? (
              <div className="p-12 text-center text-ink-soft">
                {loading ? 'Generating report…' : 'Click "Generate Report" to build a preview.'}
              </div>
            ) : tab === 'Overview' ? (
              <div className="p-6 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-ink-soft border-b border-black/10">
                      <th className="py-2 pr-4 font-medium">Metric</th>
                      <th className="py-2 font-medium">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(preview.kpis).map(([key, value]) => (
                      <tr key={key} className="border-b border-black/5 last:border-0">
                        <td className="py-2 pr-4">{formatLabel(key)}</td>
                        <td
                          className={`py-2 font-semibold ${
                            key.includes('growth') && value > 0 ? 'text-emerald-600' : ''
                          } ${key.includes('growth') && value < 0 ? 'text-danger' : ''}`}
                        >
                          {formatValue(key, value)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="mt-6 text-sm leading-relaxed text-ink-soft">{preview.insights}</p>
              </div>
            ) : (
              <iframe title="Email preview" srcDoc={preview.html} className="w-full h-[500px] border-0" />
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
