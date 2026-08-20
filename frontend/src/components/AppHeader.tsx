import { ChartBar, Moon, Sun } from '@phosphor-icons/react'
import { useTheme } from '../lib/theme'
import { Button } from './ui/button'

const NAV_LINKS = [
  { label: 'Dashboard', href: '#dashboard' },
  { label: 'Charts', href: '#charts' },
  { label: 'Data', href: '#data' },
  { label: 'Settings', href: '#settings' },
]

interface AppHeaderProps {
  onGenerateClick: () => void
  generating: boolean
}

export function AppHeader({ onGenerateClick, generating }: AppHeaderProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-6 px-6">
        <a
          href="/"
          title="Back to home and refresh"
          className="flex shrink-0 items-center gap-2 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ChartBar weight="bold" size={18} />
          </span>
          <span className="text-base font-black tracking-tight">Business Reports</span>
        </a>

        <nav className="hidden items-center gap-7 text-sm font-semibold text-muted-foreground md:flex">
          {NAV_LINKS.map((link) => (
            <a key={link.href} href={link.href} className="transition-colors hover:text-foreground">
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </Button>
          <Button onClick={onGenerateClick} disabled={generating} size="sm">
            {generating ? 'Generating…' : 'Generate Report'}
          </Button>
        </div>
      </div>
    </header>
  )
}
