interface TopBarProps {
  statusMessage: string
  onGenerateClick: () => void
  generating: boolean
}

const NAV_LINKS = [
  { label: 'Dashboard', href: '#dashboard' },
  { label: 'Charts', href: '#charts' },
  { label: 'Data', href: '#data' },
  { label: 'Settings', href: '#settings' },
]

export function TopBar({ statusMessage, onGenerateClick, generating }: TopBarProps) {
  return (
    <header className="sticky top-0 z-50">
      <div className="bg-lime text-ink text-center text-sm font-semibold py-2 px-4 border-b-2 border-ink">
        {statusMessage}
      </div>
      <nav className="bg-white/95 backdrop-blur border-b border-black/10">
        <div className="mx-auto max-w-6xl flex items-center justify-between px-6 py-4 gap-6">
          <a
            href="/"
            title="Back to home and refresh"
            className="flex items-center gap-2 shrink-0 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <rect x="3" y="12" width="4" height="9" rx="1" fill="#8B5CF6" />
              <rect x="10" y="7" width="4" height="14" rx="1" fill="#0F0F10" />
              <rect x="17" y="3" width="4" height="18" rx="1" fill="#2452D9" />
            </svg>
            <span className="text-lg font-black tracking-tight">Business Reports</span>
          </a>
          <div className="hidden md:flex items-center gap-8 text-sm font-semibold text-ink-soft">
            {NAV_LINKS.map((link) => (
              <a key={link.href} href={link.href} className="hover:text-ink transition-colors">
                {link.label}
              </a>
            ))}
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={onGenerateClick}
              disabled={generating}
              className="pill pill-primary text-sm py-2 px-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generating ? 'Generating…' : 'Generate Report'}
            </button>
          </div>
        </div>
      </nav>
    </header>
  )
}
