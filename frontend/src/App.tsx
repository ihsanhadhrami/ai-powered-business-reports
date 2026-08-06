import { useCallback, useEffect, useState } from 'react'
import {
  api,
  ApiError,
  type ConfigResponse,
  type DataInfoResponse,
  type ReportPreviewResponse,
} from './api/client'
import { TopBar } from './components/TopBar'
import { Hero } from './components/Hero'
import { KpiStrip } from './components/KpiStrip'
import { HighlightTiles } from './components/HighlightTiles'
import { ReportPreviewPanel } from './components/ReportPreviewPanel'
import { ChartsSection } from './components/ChartsSection'
import { DataUpload } from './components/DataUpload'
import { SendCta } from './components/SendCta'
import { SettingsPanel } from './components/SettingsPanel'

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
    <div className="min-h-screen">
      <TopBar
        statusMessage={
          config?.ai_enabled
            ? 'AI-powered insights are enabled for this report'
            : 'Running on deterministic local insights'
        }
        onGenerateClick={generatePreview}
        generating={previewLoading}
      />
      <Hero dataInfo={dataInfo} onGenerate={generatePreview} generating={previewLoading} />
      <KpiStrip kpis={preview?.kpis ?? null} />
      {previewError && (
        <div className="mx-auto max-w-6xl px-6 pt-6 text-sm text-danger font-medium">
          {previewError}
        </div>
      )}
      <HighlightTiles kpis={preview?.kpis ?? null} insights={preview?.insights ?? null} />
      <ReportPreviewPanel preview={preview} loading={previewLoading} onRegenerate={generatePreview} />
      <ChartsSection availableColumns={dataInfo?.columns ?? []} />
      <DataUpload dataInfo={dataInfo} onUploaded={setDataInfo} />
      <SendCta
        onSend={handleSend}
        sending={sending}
        status={sendStatus}
        emailConfigured={config?.email_configured ?? false}
      />
      <SettingsPanel config={config} />
    </div>
  )
}

export default App
