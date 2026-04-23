import type { Tier } from '@/lib/listings'

const CONFIG: Record<Tier, { label: string; className: string }> = {
  specialist: {
    label: 'ADA Specialist',
    className: 'bg-green-100 text-green-800 border border-green-200',
  },
  offers: {
    label: 'Offers ADA Services',
    className: 'bg-blue-100 text-blue-800 border border-blue-200',
  },
  unverified: {
    label: 'Local Remodeler',
    className: 'bg-gray-100 text-gray-600 border border-gray-200',
  },
}

export default function TierBadge({ tier }: { tier: Tier }) {
  const { label, className } = CONFIG[tier]
  return (
    <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${className}`}>
      {label}
    </span>
  )
}
