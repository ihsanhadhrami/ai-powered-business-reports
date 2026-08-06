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
    <section id="charts" className="mx-auto max-w-6xl px-6 py-16">
      <h2 className="text-3xl mb-6">Trends</h2>
      <div className="flex flex-wrap gap-2 mb-6">
        {columns.map((column) => (
          <button
            key={column}
            onClick={() => setActive(column)}
            className={`pill text-sm py-2 px-4 ${
              active === column ? 'bg-ink text-white' : 'bg-white border border-black/10 text-ink-soft'
            }`}
          >
            {column.replace('_', ' ')}
          </button>
        ))}
      </div>
      <div className="rounded-2xl border border-black/10 p-6 h-80">
        {chart ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} minTickGap={30} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#2452D9" strokeWidth={2} dot={false} name={active} />
              <Line
                type="monotone"
                dataKey="trend"
                stroke="#8B5CF6"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
                name="Moving average"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-ink-soft text-sm">
            Loading chart…
          </div>
        )}
      </div>
    </section>
  )
}
