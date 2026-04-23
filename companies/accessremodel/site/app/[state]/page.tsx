import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import CityGrid from '@/components/CityGrid'
import ListingCard from '@/components/ListingCard'
import {
  getStates,
  getStateBySlug,
  getCitiesForState,
  getListingsForState,
} from '@/lib/listings'

export const dynamicParams = false

export function generateStaticParams() {
  return getStates().map(s => ({ state: s.slug }))
}

interface Props {
  params: { state: string }
}

export function generateMetadata({ params }: Props): Metadata {
  const stateName = getStateBySlug(params.state)
  if (!stateName) return {}
  const count = getListingsForState(params.state).length
  return {
    title: `ADA Bathroom Contractors in ${stateName}`,
    description: `Find ${count} ADA-accessible bathroom contractors in ${stateName} specializing in aging-in-place remodeling, grab bars, roll-in showers, and walk-in tubs.`,
    openGraph: {
      title: `ADA Bathroom Contractors in ${stateName} | AccessRemodel`,
      description: `${count} contractors in ${stateName} specializing in accessible bathroom remodeling.`,
    },
  }
}

export default function StatePage({ params }: Props) {
  const stateName = getStateBySlug(params.state)
  if (!stateName) notFound()

  const allListings = getListingsForState(params.state)
  const cities = getCitiesForState(params.state)
  const specialists = allListings.filter(l => l.tier === 'specialist')

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <header className="mb-10">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
          ADA Bathroom Contractors in {stateName}
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl">
          {allListings.length} contractors in {stateName} offer accessible bathroom
          remodeling services — from certified aging-in-place specialists to general
          remodelers who include grab bars and roll-in showers. Use the city grid below to
          narrow your search.
        </p>
        <div className="flex flex-wrap gap-4 mt-4 text-sm">
          <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
            {allListings.length} total contractors
          </span>
          <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
            {specialists.length} ADA specialists
          </span>
          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
            {cities.length} cities covered
          </span>
        </div>
      </header>

      {/* City grid */}
      <div className="mb-12">
        <CityGrid cities={cities} stateSlug={params.state} />
      </div>

      {/* Specialists callout */}
      {specialists.length > 0 && (
        <section aria-labelledby="specialists-heading" className="mb-12">
          <h2 id="specialists-heading" className="text-xl font-bold text-gray-900 mb-5">
            Verified ADA Specialists in {stateName}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {specialists.map(l => (
              <ListingCard key={l.id} listing={l} />
            ))}
          </div>
        </section>
      )}

      {/* SEO copy */}
      <section className="prose prose-gray max-w-2xl mt-10 text-sm text-gray-600 leading-relaxed">
        <h2 className="text-lg font-bold text-gray-800 mb-2 not-prose">
          Finding ADA-Accessible Bathroom Remodelers in {stateName}
        </h2>
        <p>
          An aging-in-place or ADA bathroom remodel typically includes roll-in shower
          conversion, grab bar installation, curbless shower entry, raised toilets, and
          non-slip flooring. In {stateName}, {allListings.length} contractors in our
          directory offer at least some of these services — and {specialists.length} have
          been individually verified as dedicated accessibility specialists.
        </p>
        <p className="mt-3">
          When hiring, look for NAHB Certified Aging-in-Place Specialist (CAPS)
          credentials, proof of liability insurance, and local references. Our verified
          listings call out these attributes explicitly.
        </p>
      </section>
    </div>
  )
}
