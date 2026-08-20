import { PaperPlaneTilt } from '@phosphor-icons/react'
import type { ReportPreviewResponse } from '../api/client'
import { formatLabel, formatValue } from '../lib/format'
import { cn } from '../lib/utils'
import { Alert } from './ui/alert'
import { Button } from './ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './ui/card'
import { Skeleton } from './ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

interface SendStatus {
  type: 'idle' | 'success' | 'error'
  message?: string
}

interface ReportPreviewPanelProps {
  preview: ReportPreviewResponse | null
  loading: boolean
  onRegenerate: () => void
  onSend: () => void
  sending: boolean
  sendStatus: SendStatus
  emailConfigured: boolean
}

export function ReportPreviewPanel({
  preview,
  loading,
  onRegenerate,
  onSend,
  sending,
  sendStatus,
  emailConfigured,
}: ReportPreviewPanelProps) {
  return (
    <Card id="dashboard">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle>Report preview</CardTitle>
        <Button variant="outline" size="sm" onClick={onRegenerate} disabled={loading}>
          {loading ? 'Regenerating…' : 'Regenerate'}
        </Button>
      </CardHeader>
      <CardContent>
        {!preview ? (
          loading ? (
            <div className="space-y-3 py-6">
              <Skeleton className="h-6 w-1/2" />
              <Skeleton className="h-32 w-full" />
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center gap-1 py-16 text-center">
              <p className="text-sm font-semibold">No report generated yet</p>
              <p className="text-sm text-muted-foreground">Click "Generate Report" to build a preview.</p>
            </div>
          )
        ) : (
          <Tabs defaultValue="overview">
            <TabsList className="mb-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="email">Email preview</TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <div className="overflow-x-auto rounded-xl border border-border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-muted-foreground">
                      <th className="px-4 py-2.5 font-medium">Metric</th>
                      <th className="px-4 py-2.5 font-medium">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(preview.kpis).map(([key, value]) => (
                      <tr key={key} className="border-b border-border last:border-0">
                        <td className="px-4 py-2.5">{formatLabel(key)}</td>
                        <td
                          className={cn(
                            'px-4 py-2.5 font-semibold',
                            key.includes('growth') && value > 0 && 'text-success',
                            key.includes('growth') && value < 0 && 'text-destructive',
                          )}
                        >
                          {formatValue(key, value)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">{preview.insights}</p>
            </TabsContent>

            <TabsContent value="email">
              <div className="overflow-hidden rounded-xl border border-border">
                <div className="flex items-center gap-2 border-b border-border bg-secondary px-4 py-2.5">
                  <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
                  <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
                  <span className="h-3 w-3 rounded-full bg-[#28c840]" />
                  <span className="ml-2 truncate text-xs text-muted-foreground">{preview.subject}</span>
                </div>
                <iframe
                  title="Email preview"
                  srcDoc={preview.html}
                  className="h-125 w-full border-0 bg-white"
                />
              </div>
            </TabsContent>
          </Tabs>
        )}
      </CardContent>

      {preview && (
        <CardFooter className="flex-col items-stretch gap-3 border-t border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-muted-foreground">
            {emailConfigured
              ? 'Ready to send to the configured recipients.'
              : "Email isn't configured on the backend yet."}
          </p>
          <Button onClick={onSend} disabled={sending || !emailConfigured} className="gap-2">
            <PaperPlaneTilt size={16} weight="bold" />
            {sending ? 'Sending…' : 'Send Report'}
          </Button>
        </CardFooter>
      )}

      {sendStatus.type !== 'idle' && (
        <div className="px-6 pb-6">
          <Alert variant={sendStatus.type === 'success' ? 'success' : 'destructive'}>
            {sendStatus.message}
          </Alert>
        </div>
      )}
    </Card>
  )
}
