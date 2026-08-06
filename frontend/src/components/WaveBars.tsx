interface WaveBarsProps {
  variant?: 'light' | 'dark'
  className?: string
  barCount?: number
}

/**
 * The vertical-bar "waveform" motif used throughout the semrush.com
 * reference (hero background, enterprise section). Heights are a
 * deterministic pseudo-random sequence so the pattern looks organic
 * without needing real data or client-only randomness.
 */
export function WaveBars({ variant = 'light', className = '', barCount = 90 }: WaveBarsProps) {
  const gradientId = `wave-${variant}`
  const bars = Array.from({ length: barCount }, (_, i) => {
    const seed = Math.sin(i * 12.9898) * 43758.5453
    const frac = seed - Math.floor(seed)
    return 15 + frac * 85
  })

  return (
    <svg
      viewBox="0 0 900 120"
      preserveAspectRatio="none"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={variant === 'dark' ? '#2dd4bf' : '#5eead4'} />
          <stop offset="100%" stopColor={variant === 'dark' ? '#8b5cf6' : '#c4b5fd'} />
        </linearGradient>
      </defs>
      {bars.map((height, i) => {
        const barWidth = 900 / barCount - 2
        const x = i * (900 / barCount)
        const barHeight = (height / 100) * 120
        return (
          <rect
            key={i}
            x={x}
            y={120 - barHeight}
            width={Math.max(barWidth, 1)}
            height={barHeight}
            fill={`url(#${gradientId})`}
            opacity={variant === 'dark' ? 0.85 : 0.5}
          />
        )
      })}
    </svg>
  )
}
