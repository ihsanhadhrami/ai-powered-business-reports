import { WaveBars } from './WaveBars'

interface SendStatus {
  type: 'idle' | 'success' | 'error'
  message?: string
}

interface SendCtaProps {
  onSend: () => void
  sending: boolean
  status: SendStatus
  emailConfigured: boolean
}

export function SendCta({ onSend, sending, status, emailConfigured }: SendCtaProps) {
  return (
    <section className="relative overflow-hidden bg-ink text-white py-20">
      <WaveBars variant="dark" className="absolute inset-0 w-full h-full opacity-70" />
      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <h2 className="text-4xl md:text-5xl text-white mb-4">Automate your reporting.</h2>
        <p className="text-white/70 text-lg mb-8 max-w-xl mx-auto">
          Every period, every metric — sent straight to your inbox with AI-written insights.
        </p>
        {!emailConfigured && (
          <p className="text-warn text-sm mb-4">
            Email isn't configured on the backend yet (set EMAIL_SENDER / EMAIL_PASSWORD).
          </p>
        )}
        <button
          onClick={onSend}
          disabled={sending || !emailConfigured}
          className="pill pill-outline-white disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {sending ? 'Sending…' : 'Send Report Now'}
        </button>
        {status.type === 'success' && (
          <p className="mt-4 text-lime font-semibold">{status.message}</p>
        )}
        {status.type === 'error' && (
          <p className="mt-4 text-danger font-semibold">{status.message}</p>
        )}
      </div>
    </section>
  )
}
