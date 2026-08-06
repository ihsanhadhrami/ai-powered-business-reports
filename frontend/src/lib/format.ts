export function formatLabel(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export function formatValue(key: string, value: number): string {
  if (key.includes('growth')) {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
  }
  if (key.includes('revenue') || key.includes('per_customer')) {
    return `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
  }
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 })
}
