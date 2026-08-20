import type { ConfigResponse } from '../api/client'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Skeleton } from './ui/skeleton'

export function SettingsPanel({ config }: { config: ConfigResponse | null }) {
  return (
    <Card id="settings">
      <CardHeader>
        <CardTitle>Settings</CardTitle>
      </CardHeader>
      <CardContent>
        {!config ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        ) : (
          <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ['Report frequency', config.report_frequency],
              ['Report time', config.report_time],
              ['AI insights', config.ai_enabled ? 'Enabled' : 'Disabled (local insights)'],
              ['Email', config.email_configured ? 'Configured' : 'Not configured'],
            ].map(([label, value]) => (
              <div key={label} className="rounded-xl border border-border p-4">
                <dt className="mb-1 text-xs font-medium text-muted-foreground">{label}</dt>
                <dd className="font-bold">{value}</dd>
              </div>
            ))}
          </dl>
        )}
      </CardContent>
    </Card>
  )
}
