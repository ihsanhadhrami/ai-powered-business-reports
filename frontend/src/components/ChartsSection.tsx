import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api, type ChartResponse } from '../api/client'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Skeleton } from './ui/skeleton'
import { Tabs, TabsList, TabsTrigger } from './ui/tabs'

const METRICS = ['Revenue', 'Sales', 'Customer_Count'] as const

interface ChartsSectionProps {
  availableColumns: string[]
}

export function ChartsSection({ availableColumns }: ChartsSectionProps) {
  const columns = METRICS.filter((metric) => availableColumns.includes(metric))
  const [charts, setCharts] = useState<Record<string, ChartResponse>>({})
  const [active, setActive] = useState<string | null>(null)

  useEffect(() => {
    if (columns.length === 0) return
    setActive((current) => (current && columns.includes(current as (typeof columns)[number]) ? current : columns[0]))
    columns.forEach((column) => {
      api
        .getChart(column)
        .then((data) => setCharts((prev) => ({ ...prev, [column]: data })))
        .catch(() => {})
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [availableColumns.join(',')])

  if (columns.length === 0 || !active) return null

  const chart = charts[active]
  const chartData = chart
    ? chart.dates.map((date, i) => ({
        date,
        value: chart.values[i],
        trend: chart.moving_average[i],
      }))
    : []

  return (
    <Card id="charts">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle>Trends</CardTitle>
        <Tabs value={active} onValueChange={setActive}>
          <TabsList>
            {columns.map((column) => (
              <TabsTrigger key={column} value={column}>
                {column.replace('_', ' ')}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </CardHeader>
      <CardContent className="h-80">
        {chart ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                minTickGap={30}
                axisLine={{ stroke: 'hsl(var(--border))' }}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.75rem',
                  color: 'hsl(var(--foreground))',
                  fontSize: '0.875rem',
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="hsl(var(--primary))"
                strokeWidth={2.5}
                dot={false}
                name={active}
              />
              <Line
                type="monotone"
                dataKey="trend"
                stroke="hsl(var(--muted-foreground))"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
                name="Moving average"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <Skeleton className="h-full w-full" />
        )}
      </CardContent>
    </Card>
  )
}
