import React from 'react'

/* ─── Base Skeleton ─────────────────────────────────────────── */
const Skeleton = React.forwardRef(({ className = '', ...props }, ref) => (
  <div
    ref={ref}
    aria-hidden="true"
    className={`skeleton rounded ${className}`}
    {...props}
  />
))
Skeleton.displayName = 'Skeleton'

/* ─── Text block (multiple lines) ──────────────────────────── */
export const SkeletonText = ({ lines = 3, className = '' }) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton
        key={i}
        className={`h-4 ${i === lines - 1 ? 'w-3/4' : 'w-full'}`}
      />
    ))}
  </div>
)

/* ─── Single table row ──────────────────────────────────────── */
export const SkeletonTableRow = ({ cols = 5, hasAvatar = false }) => (
  <tr className="border-b border-ink-50">
    {Array.from({ length: cols }).map((_, i) => (
      <td key={i} className="px-4 py-3">
        {i === 0 && hasAvatar ? (
          <div className="flex items-center gap-2.5">
            <Skeleton className="w-7 h-7 rounded-full shrink-0" />
            <Skeleton className="h-4 w-28 rounded" />
          </div>
        ) : i === cols - 1 ? (
          <Skeleton className="h-4 w-16 rounded ml-auto" />
        ) : (
          <Skeleton className={`h-4 rounded ${[, 'w-36', 'w-24', 'w-20', 'w-14'][i] || 'w-full'}`} />
        )}
      </td>
    ))}
  </tr>
)

/* ─── Full skeleton table body ──────────────────────────────── */
export const SkeletonTable = ({ rows = 7, cols = 5, hasAvatar = false }) => (
  <>
    {Array.from({ length: rows }).map((_, i) => (
      <SkeletonTableRow key={i} cols={cols} hasAvatar={hasAvatar} />
    ))}
  </>
)

/* ─── Stat/metric card skeleton ─────────────────────────────── */
export const SkeletonMetricCard = ({ className = '' }) => (
  <div className={`bg-surface border border-ink-100 rounded-xl p-5 ${className}`}>
    <div className="flex items-center justify-between mb-4">
      <Skeleton className="h-3 w-24 rounded" />
      <Skeleton className="w-8 h-8 rounded-lg" />
    </div>
    <Skeleton className="h-9 w-20 rounded mb-3" />
    <Skeleton className="h-5 w-16 rounded-full" />
  </div>
)

/* ─── Generic card skeleton ─────────────────────────────────── */
export const SkeletonCard = ({ className = '' }) => (
  <div className={`bg-surface border border-ink-100 rounded-xl p-5 space-y-4 ${className}`}>
    <div className="flex items-center gap-3">
      <Skeleton className="w-10 h-10 rounded-full shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-1/3 rounded" />
        <Skeleton className="h-3 w-1/2 rounded" />
      </div>
    </div>
    <SkeletonText lines={2} />
  </div>
)

export default Skeleton
