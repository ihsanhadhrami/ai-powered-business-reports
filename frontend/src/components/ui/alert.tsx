import { forwardRef, type HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/utils'

const alertVariants = cva('flex items-start gap-3 rounded-xl border p-4 text-sm', {
  variants: {
    variant: {
      default: 'border-border bg-secondary/60 text-foreground',
      destructive: 'border-destructive/30 bg-destructive/10 text-destructive',
      success: 'border-success/30 bg-success/10 text-success',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
})

export interface AlertProps extends HTMLAttributes<HTMLDivElement>, VariantProps<typeof alertVariants> {}

export const Alert = forwardRef<HTMLDivElement, AlertProps>(({ className, variant, ...props }, ref) => (
  <div ref={ref} role="status" className={cn(alertVariants({ variant, className }))} {...props} />
))
Alert.displayName = 'Alert'
