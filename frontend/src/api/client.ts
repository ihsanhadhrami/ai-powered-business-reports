export interface ConfigResponse {
  report_frequency: string
  report_time: string
  ai_enabled: boolean
  email_configured: boolean
}

export interface DataInfoResponse {
  rows: number
  columns: string[]
  date_min: string
  date_max: string
}

export interface ReportPreviewResponse {
  kpis: Record<string, number>
  insights: string
  subject: string
  html: string
}

export interface SendReportResponse {
  success: boolean
  message: string
}

export interface ChartResponse {
  column: string
  dates: string[]
  values: number[]
  moving_average: number[]
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const API_KEY = import.meta.env.VITE_API_KEY

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  if (API_KEY) headers.set('X-API-Key', API_KEY)
  if (init?.body && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${BASE_URL}${path}`, { ...init, headers })
  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new ApiError(detail?.detail ?? response.statusText, response.status)
  }
  return response.json() as Promise<T>
}

export const api = {
  getConfig: () => request<ConfigResponse>('/api/config'),
  getData: () => request<DataInfoResponse>('/api/data'),
  uploadData: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request<DataInfoResponse>('/api/data/upload', { method: 'POST', body: formData })
  },
  getChart: (column: string) => request<ChartResponse>(`/api/charts/${column}`),
  previewReport: () => request<ReportPreviewResponse>('/api/reports/preview'),
  sendReport: (recipients?: string[]) =>
    request<SendReportResponse>('/api/reports/send', {
      method: 'POST',
      body: JSON.stringify({ recipients: recipients ?? null }),
    }),
}
