import { TrendDown, TrendUp } from '@phosphor-icons/react'
import { formatLabel, formatValue } from '../lib/format'
import { Badge } from './ui/badge'
import { Card, CardContent } from './ui/card'
import { Skeleton } from './ui/skeleton'

interface KpiGridProps {
  kpis: Record<string, number> | null
  loading: boolean
}

// Headline metrics only, in a fixed order that fills the 4-column grid exactly.
// The complete KPI set (including averages and growth rates) is listed in the
// report preview table below, so nothing is hidden from the user.
const HEADLINE_KPIS: { key: string; growthKey?: string }[] = [
  { key: 'total_revenue', growthKey: 'revenue_growth' },
  { key: 'total_sales', growthKey: 'sales_growth' },
  { key: 'total_customers', growthKey: 'customer_growth' },
  { key: 'avg_revenue_per_customer' },
]

function GrowthBadge({ value }: { value: number }) {
  if (value === 0) return null
  const positive = value > 0
  return (
    <Badge variant={positive ? 'success' : 'destructive'} className="gap-1">
      {positive ? <TrendUp size={12} weight="bold" /> : <TrendDown size={12} weight="bold" />}
      {formatValue('growth', value)}
    </Badge>
  )
}

export function KpiGrid({ kpis, loading }: KpiGridProps) {
  if (loading && !kpis) {
    return (
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {HEADLINE_KPIS.map(({ key }) => (
          <Card key={key}>
            <CardContent className="p-5">
              <Skeleton className="mb-3 h-4 w-20" />
              <Skeleton className="h-7 w-24" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!kpis) {
    return (
      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center justify-center gap-1 py-10 text-center">
          <p className="text-sm font-semibold">No report generated yet</p>
          <p className="text-sm text-muted-foreground">Click "Generate Report" to calculate your KPIs.</p>
        </CardContent>
      </Card>
    )
  }

  const cards = HEADLINE_KPIS.filter(({ key }) => typeof kpis[key] === 'number')

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map(({ key, growthKey }) => {
        const growth = growthKey ? kpis[growthKey] : undefined
        return (
          <Card key={key}>
            <CardContent className="p-5">
              <p className="mb-2 text-xs font-medium text-muted-foreground">{formatLabel(key)}</p>
              <p className="text-2xl font-bold tracking-tight">{formatValue(key, kpis[key])}</p>
              {typeof growth === 'number' && (
                <div className="mt-2">
                  <GrowthBadge value={growth} />
                </div>
              )}
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
