import { useCallback, useEffect, useState } from 'react'
import {
  api,
  ApiError,
  type ConfigResponse,
  type DataInfoResponse,
  type ReportPreviewResponse,
} from './api/client'
import { AppHeader } from './components/AppHeader'
import { ChartsSection } from './components/ChartsSection'
import { DashboardHeader } from './components/DashboardHeader'
import { DataUpload } from './components/DataUpload'
import { InsightCard } from './components/InsightCard'
import { KpiGrid } from './components/KpiGrid'
import { ReportPreviewPanel } from './components/ReportPreviewPanel'
import { SettingsPanel } from './components/SettingsPanel'
import { Alert } from './components/ui/alert'

type SendStatus = { type: 'idle' | 'success' | 'error'; message?: string }

function App() {
  const [config, setConfig] = useState<ConfigResponse | null>(null)
  const [dataInfo, setDataInfo] = useState<DataInfoResponse | null>(null)
  const [preview, setPreview] = useState<ReportPreviewResponse | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const [sendStatus, setSendStatus] = useState<SendStatus>({ type: 'idle' })

  useEffect(() => {
    api.getConfig().then(setConfig).catch(() => {})
    api.getData().then(setDataInfo).catch(() => {})
  }, [])

  const generatePreview = useCallback(async () => {
    setPreviewLoading(true)
    setPreviewError(null)
    try {
      const result = await api.previewReport()
      setPreview(result)
    } catch (err) {
      setPreviewError(err instanceof ApiError ? err.message : 'Failed to generate report')
    } finally {
      setPreviewLoading(false)
    }
  }, [])

  const handleSend = useCallback(async () => {
    setSending(true)
    setSendStatus({ type: 'idle' })
    try {
      const result = await api.sendReport()
      setSendStatus({ type: 'success', message: result.message })
    } catch (err) {
      setSendStatus({
        type: 'error',
        message: err instanceof ApiError ? err.message : 'Failed to send report',
      })
    } finally {
      setSending(false)
    }
  }, [])

  return (
    <div className="min-h-dvh">
      <AppHeader onGenerateClick={generatePreview} generating={previewLoading} />

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">
        <DashboardHeader
          dataInfo={dataInfo}
          aiEnabled={config?.ai_enabled ?? null}
          onGenerate={generatePreview}
          generating={previewLoading}
        />

        {previewError && <Alert variant="destructive">{previewError}</Alert>}

        <KpiGrid kpis={preview?.kpis ?? null} loading={previewLoading} />

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <InsightCard insights={preview?.insights ?? null} loading={previewLoading} />
          </div>
          <div className="lg:col-span-2">
            <ChartsSection availableColumns={dataInfo?.columns ?? []} />
          </div>
        </div>

        <ReportPreviewPanel
          preview={preview}
          loading={previewLoading}
          onRegenerate={generatePreview}
          onSend={handleSend}
          sending={sending}
          sendStatus={sendStatus}
          emailConfigured={config?.email_configured ?? false}
        />

        <div className="grid gap-6 lg:grid-cols-2">
          <DataUpload dataInfo={dataInfo} onUploaded={setDataInfo} />
          <SettingsPanel config={config} />
        </div>
      </main>
    </div>
  )
}

export default App
