import type { Metadata } from 'next'
import Link from 'next/link'
import Hero from '@/components/Hero'
import StateGrid from '@/components/StateGrid'
import ListingCard from '@/components/ListingCard'
import { listings, getStates } from '@/lib/listings'

export const metadata: Metadata = {
  title: 'AccessRemodel — Find ADA Bathroom Contractors',
  description:
    '247 vetted contractors across 11 states specializing in aging-in-place bathroom remodeling. Find grab bar installers, roll-in shower specialists, and walk-in tub contractors near you.',
}

export default function HomePage() {
  const states = getStates()
  const specialists = listings.filter(l => l.tier === 'specialist')

  return (
    <>
      <Hero states={states} />

      {/* Featured Specialists */}
      <section className="max-w-6xl mx-auto px-4 py-14" aria-labelledby="specialists-heading">
        <div className="flex items-baseline justify-between mb-6">
          <h2 id="specialists-heading" className="text-2xl font-bold text-gray-900">
            Featured ADA Specialists
          </h2>
          <span className="text-sm text-gray-500">{specialists.length} verified specialists</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {specialists.map(l => (
            <ListingCard key={l.id} listing={l} />
          ))}
        </div>
      </section>

      {/* Value Props */}
      <section
        className="bg-white border-y border-gray-200 py-14 px-4"
        aria-labelledby="why-heading"
      >
        <div className="max-w-6xl mx-auto">
          <h2 id="why-heading" className="text-2xl font-bold text-gray-900 text-center mb-10">
            Why Use AccessRemodel?
          </h2>
          <ul className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: '✓',
                title: 'Verified Specialists',
                body: 'Our Specialist tier contractors are individually reviewed for ADA-specific experience — grab bars, roll-in showers, and aging-in-place remodeling.',
              },
              {
                icon: '⚡',
                title: 'Fast, Focused Results',
                body: 'Every contractor in our directory is pre-filtered for accessibility services — no generic remodelers mixed in.',
              },
              {
                icon: '♿',
                title: 'Accessibility-First',
                body: 'We surface CAPS-certified contractors and call out specific services like ramp installation, widened doorways, and non-slip flooring.',
              },
            ].map(({ icon, title, body }) => (
              <li
                key={title}
                className="flex flex-col items-center text-center gap-3 p-6 rounded-xl bg-gray-50"
              >
                <span className="text-3xl" aria-hidden="true">{icon}</span>
                <h3 className="font-bold text-lg text-gray-900">{title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{body}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* State Grid */}
      <section className="max-w-6xl mx-auto px-4 py-14">
        <StateGrid states={states} />
      </section>

      {/* CTA */}
      <section className="bg-primary-50 border border-primary-200 rounded-2xl max-w-2xl mx-auto mx-4 mb-14 px-8 py-10 text-center">
        <h2 className="text-xl font-bold text-primary-800 mb-2">Are you an ADA contractor?</h2>
        <p className="text-primary-700 mb-5 text-sm">
          Claim your listing to verify your credentials, update your services, and start
          receiving direct leads.
        </p>
        <Link
          href="/claim"
          className="inline-block bg-primary-600 hover:bg-primary-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
        >
          Claim Your Listing →
        </Link>
      </section>
    </>
  )
}
