import { useState } from 'react'
import { api, ApiError, type DataInfoResponse } from '../api/client'

interface DataUploadProps {
  dataInfo: DataInfoResponse | null
  onUploaded: (info: DataInfoResponse) => void
}

export function DataUpload({ dataInfo, onUploaded }: DataUploadProps) {
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  async function handleFile(file: File) {
    setError(null)
    setUploading(true)
    try {
      const info = await api.uploadData(file)
      onUploaded(info)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <section id="data" className="mx-auto max-w-6xl px-6 py-16">
      <h2 className="text-3xl mb-6">Data</h2>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-black/10 p-6">
          <div className="text-sm text-ink-soft mb-2">Current data source</div>
          {dataInfo ? (
            <>
              <div className="text-lg font-bold">{dataInfo.rows} rows</div>
              <div className="text-sm text-ink-soft">
                {dataInfo.date_min} → {dataInfo.date_max}
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {dataInfo.columns.map((col) => (
                  <span
                    key={col}
                    className="text-xs font-medium bg-mint-tint text-ink px-3 py-1 rounded-full"
                  >
                    {col}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <div className="text-ink-soft">No data loaded</div>
          )}
        </div>
        <label className="rounded-2xl border-2 border-dashed border-black/15 p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:border-violet transition-colors">
          <span className="font-semibold mb-1">Upload a CSV</span>
          <span className="text-sm text-ink-soft mb-3">
            Requires a Date column, plus any of Revenue / Sales / Customer_Count
          </span>
          <span className="pill pill-outline text-sm py-2 px-4">
            {uploading ? 'Uploading…' : 'Choose file'}
          </span>
          <input
            type="file"
            accept=".csv"
            className="hidden"
            disabled={uploading}
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleFile(file)
              e.target.value = ''
            }}
          />
        </label>
      </div>
      {error && <p className="mt-4 text-sm text-danger font-medium">{error}</p>}
    </section>
  )
}
