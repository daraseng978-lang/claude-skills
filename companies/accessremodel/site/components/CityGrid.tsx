import Link from 'next/link'
import type { CityInfo } from '@/lib/listings'

interface Props {
  cities: CityInfo[]
  stateSlug: string
}

export default function CityGrid({ cities, stateSlug }: Props) {
  return (
    <section aria-label="Browse by city">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Browse by City</h2>
      <ul className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {cities.map(c => (
          <li key={c.slug}>
            <Link
              href={`/${stateSlug}/${c.slug}`}
              className="flex flex-col p-3 rounded-lg border border-gray-200 hover:border-primary-600 hover:bg-primary-50 transition-all"
              aria-label={`${c.name} — ${c.count} contractors`}
            >
              <span className="font-medium text-gray-900 text-sm">{c.name}</span>
              <span className="text-xs text-gray-500 mt-0.5">{c.count} contractors</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
