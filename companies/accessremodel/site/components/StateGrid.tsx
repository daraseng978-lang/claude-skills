import Link from 'next/link'
import type { StateInfo } from '@/lib/listings'

export default function StateGrid({ states }: { states: StateInfo[] }) {
  return (
    <section aria-label="Browse by state">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Browse by State</h2>
      <ul className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {states.map(s => (
          <li key={s.slug}>
            <Link
              href={`/${s.slug}`}
              className="flex flex-col items-center justify-center p-4 rounded-xl border-2 border-gray-200 hover:border-primary-600 hover:bg-primary-50 transition-all min-h-[80px] text-center"
              aria-label={`${s.name} — ${s.count} contractors`}
            >
              <span className="font-semibold text-gray-900">{s.name}</span>
              <span className="text-sm text-gray-500 mt-0.5">{s.count} contractors</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
