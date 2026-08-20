import { Sparkle } from '@phosphor-icons/react'
import type { DataInfoResponse } from '../api/client'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Skeleton } from './ui/skeleton'

interface DashboardHeaderProps {
  dataInfo: DataInfoResponse | null
  aiEnabled: boolean | null
  onGenerate: () => void
  generating: boolean
}

export function DashboardHeader({ dataInfo, aiEnabled, onGenerate, generating }: DashboardHeaderProps) {
  return (
    <div className="flex flex-col gap-4 pt-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <div className="mb-2 flex items-center gap-2">
          <h1 className="text-3xl font-black tracking-tight">Overview</h1>
          {aiEnabled !== null && (
            <Badge variant={aiEnabled ? 'primary' : 'default'} className="gap-1">
              <Sparkle size={12} weight="fill" />
              {aiEnabled ? 'AI insights' : 'Local insights'}
            </Badge>
          )}
        </div>
        {dataInfo ? (
          <p className="text-sm text-muted-foreground">
            {dataInfo.rows} rows · {dataInfo.date_min} to {dataInfo.date_max}
          </p>
        ) : (
          <Skeleton className="h-5 w-56" />
        )}
      </div>
      <Button onClick={onGenerate} disabled={generating} size="lg">
        {generating ? 'Generating…' : 'Generate Report'}
      </Button>
    </div>
  )
}
