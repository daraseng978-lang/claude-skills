import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import ListingCard from '@/components/ListingCard'
import TierBadge from '@/components/TierBadge'
import {
  getStates,
  getStateBySlug,
  getCitiesForState,
  getListingsForCity,
  TIER_ORDER,
  type Tier,
} from '@/lib/listings'

export const dynamicParams = false

export function generateStaticParams() {
  const params: { state: string; city: string }[] = []
  for (const stateObj of getStates()) {
    for (const cityObj of getCitiesForState(stateObj.slug)) {
      params.push({ state: stateObj.slug, city: cityObj.slug })
    }
  }
  return params
}

interface Props {
  params: { state: string; city: string }
}

export function generateMetadata({ params }: Props): Metadata {
  const stateName = getStateBySlug(params.state)
  const cityListings = getListingsForCity(params.state, params.city)
  if (!stateName || cityListings.length === 0) return {}
  const cityName = cityListings[0]?.city ?? params.city
  const count = cityListings.length
  return {
    title: `ADA Bathroom Contractors in ${cityName}, ${stateName}`,
    description: `${count} ADA-accessible bathroom contractors in ${cityName}, ${stateName}. Find grab bar installers, roll-in shower specialists, and aging-in-place remodelers.`,
    openGraph: {
      title: `ADA Bathroom Contractors in ${cityName}, ${stateName} | AccessRemodel`,
      description: `${count} contractors in ${cityName} specializing in accessible bathroom remodeling.`,
    },
  }
}

const TIER_LABELS: Record<Tier, string> = {
  specialist: 'ADA Specialists',
  offers: 'Contractors Offering ADA Services',
  unverified: 'Local Remodelers',
}

export default function CityPage({ params }: Props) {
  const stateName = getStateBySlug(params.state)
  const cityListings = getListingsForCity(params.state, params.city)

  if (!stateName || cityListings.length === 0) notFound()

  const cityName = cityListings[0]?.city ?? params.city

  const grouped = TIER_ORDER.reduce<Record<Tier, typeof cityListings>>(
    (acc, tier) => {
      acc[tier] = cityListings.filter(l => l.tier === tier)
      return acc
    },
    { specialist: [], offers: [], unverified: [] },
  )

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="text-sm text-gray-500 mb-6">
        <ol className="flex items-center gap-1.5">
          <li><Link href="/" className="hover:text-primary-600">Home</Link></li>
          <li aria-hidden="true">›</li>
          <li>
            <Link href={`/${params.state}`} className="hover:text-primary-600">
              {stateName}
            </Link>
          </li>
          <li aria-hidden="true">›</li>
          <li aria-current="page" className="text-gray-900 font-medium">{cityName}</li>
        </ol>
      </nav>

      <header className="mb-10">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
          ADA Bathroom Contractors in {cityName}, {stateName}
        </h1>
        <p className="text-gray-600 max-w-2xl">
          {cityListings.length} contractor{cityListings.length !== 1 ? 's' : ''} in{' '}
          {cityName} offer accessible bathroom remodeling services.
        </p>
        <div className="flex flex-wrap gap-2 mt-3">
          {TIER_ORDER.map(tier =>
            grouped[tier].length > 0 ? (
              <span key={tier} className="flex items-center gap-1.5 text-sm">
                <TierBadge tier={tier} />
                <span className="text-gray-500">{grouped[tier].length}</span>
              </span>
            ) : null,
          )}
        </div>
      </header>

      {TIER_ORDER.map(tier =>
        grouped[tier].length > 0 ? (
          <section key={tier} className="mb-12" aria-labelledby={`tier-${tier}`}>
            <h2
              id={`tier-${tier}`}
              className="text-xl font-bold text-gray-900 mb-5 flex items-center gap-3"
            >
              {TIER_LABELS[tier]}
              <TierBadge tier={tier} />
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {grouped[tier].map(l => (
                <ListingCard key={l.id} listing={l} />
              ))}
            </div>
          </section>
        ) : null,
      )}
    </div>
  )
}
