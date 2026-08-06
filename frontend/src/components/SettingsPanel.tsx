import type { ConfigResponse } from '../api/client'

export function SettingsPanel({ config }: { config: ConfigResponse | null }) {
  return (
    <section id="settings" className="mx-auto max-w-6xl px-6 py-16">
      <h2 className="text-3xl mb-6">Settings</h2>
      {!config ? (
        <p className="text-ink-soft">Loading…</p>
      ) : (
        <dl className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            ['Report Frequency', config.report_frequency],
            ['Report Time', config.report_time],
            ['AI Insights', config.ai_enabled ? 'Enabled' : 'Disabled (local insights)'],
            ['Email', config.email_configured ? 'Configured' : 'Not configured'],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-black/10 p-5">
              <dt className="text-xs text-ink-soft mb-1">{label}</dt>
              <dd className="text-lg font-bold">{value}</dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  )
}
