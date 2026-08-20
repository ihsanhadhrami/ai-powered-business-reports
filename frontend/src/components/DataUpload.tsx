import { useState } from 'react'
import { UploadSimple } from '@phosphor-icons/react'
import { api, ApiError, type DataInfoResponse } from '../api/client'
import { Alert } from './ui/alert'
import { Badge } from './ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

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
    <Card id="data">
      <CardHeader>
        <CardTitle>Data source</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-border p-5">
          <p className="mb-2 text-xs font-medium text-muted-foreground">Currently loaded</p>
          {dataInfo ? (
            <>
              <p className="text-lg font-bold">{dataInfo.rows} rows</p>
              <p className="text-sm text-muted-foreground">
                {dataInfo.date_min} to {dataInfo.date_max}
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {dataInfo.columns.map((col) => (
                  <Badge key={col} variant="success">
                    {col}
                  </Badge>
                ))}
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">No data loaded</p>
          )}
        </div>

        <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border p-5 text-center transition-colors hover:border-primary">
          <UploadSimple size={22} className="text-muted-foreground" />
          <span className="text-sm font-semibold">
            {uploading ? 'Uploading…' : 'Upload a CSV'}
          </span>
          <span className="text-xs text-muted-foreground">
            Requires a Date column, plus any of Revenue / Sales / Customer_Count
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
      </CardContent>
      {error && (
        <CardContent className="pt-0">
          <Alert variant="destructive">{error}</Alert>
        </CardContent>
      )}
    </Card>
  )
}
