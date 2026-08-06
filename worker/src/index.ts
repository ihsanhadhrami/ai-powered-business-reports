export interface Env {
  ASSETS: Fetcher
  BACKEND_URL: string
  API_AUTH_TOKEN?: string
}

async function proxyToBackend(request: Request, url: URL, env: Env): Promise<Response> {
  const target = new URL(url.pathname + url.search, env.BACKEND_URL)

  const headers = new Headers(request.headers)
  headers.delete('host')
  if (env.API_AUTH_TOKEN) headers.set('X-API-Key', env.API_AUTH_TOKEN)

  const hasBody = request.method !== 'GET' && request.method !== 'HEAD'
  const body = hasBody ? await request.arrayBuffer() : undefined

  const backendResponse = await fetch(target.toString(), {
    method: request.method,
    headers,
    body,
  })

  return new Response(backendResponse.body, {
    status: backendResponse.status,
    statusText: backendResponse.statusText,
    headers: backendResponse.headers,
  })
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)

    if (url.pathname.startsWith('/api/')) {
      return proxyToBackend(request, url, env)
    }

    return env.ASSETS.fetch(request)
  },
} satisfies ExportedHandler<Env>
