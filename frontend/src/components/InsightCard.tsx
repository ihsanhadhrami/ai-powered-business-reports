import { Sparkle } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Skeleton } from './ui/skeleton'

interface InsightCardProps {
  insights: string | null
  loading: boolean
}

export function InsightCard({ insights, loading }: InsightCardProps) {
  return (
    <Card className="flex flex-col bg-primary/10">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkle size={18} weight="fill" className="text-primary" />
          Report insights
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1">
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        ) : insights ? (
          <p className="text-sm leading-relaxed">{insights}</p>
        ) : (
          <p className="text-sm text-muted-foreground">
            Generate a report to see AI-written insights here.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
