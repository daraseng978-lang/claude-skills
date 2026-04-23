import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import TierBadge from '@/components/TierBadge'
import { listings, getListingById, SERVICE_LABELS, slugify } from '@/lib/listings'

export const dynamicParams = false

export function generateStaticParams() {
  return listings.map(l => ({ slug: l.id }))
}

interface Props {
  params: { slug: string }
}

export function generateMetadata({ params }: Props): Metadata {
  const listing = getListingById(params.slug)
  if (!listing) return {}
  return {
    title: `${listing.name} — ADA Contractor in ${listing.city}, ${listing.state}`,
    description: `${listing.name} is an accessible bathroom contractor in ${listing.city}, ${listing.state}. Services include ${listing.services.map(s => SERVICE_LABELS[s] ?? s).join(', ') || 'bathroom remodeling'}.`,
    openGraph: {
      title: `${listing.name} | AccessRemodel`,
      description: `ADA contractor in ${listing.city}, ${listing.state}`,
    },
  }
}

function JsonLd({ listing }: { listing: NonNullable<ReturnType<typeof getListingById>> }) {
  const schema: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: listing.name,
    address: {
      '@type': 'PostalAddress',
      streetAddress: listing.address,
      addressLocality: listing.city,
      addressRegion: listing.state,
      postalCode: listing.postal_code,
      addressCountry: 'US',
    },
    ...(listing.phone ? { telephone: listing.phone } : {}),
    ...(listing.website ? { url: listing.website } : {}),
    ...(listing.lat !== null && listing.lng !== null
      ? { geo: { '@type': 'GeoCoordinates', latitude: listing.lat, longitude: listing.lng } }
      : {}),
    ...(listing.rating !== null && listing.reviews > 0
      ? {
          aggregateRating: {
            '@type': 'AggregateRating',
            ratingValue: listing.rating,
            reviewCount: listing.reviews,
          },
        }
      : {}),
  }
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  )
}

export default function ListingPage({ params }: Props) {
  const listing = getListingById(params.slug)
  if (!listing) notFound()

  const stateSlug = slugify(listing.state)
  const citySlug = slugify(listing.city)
  const isVerified = listing.tier !== 'unverified'

  return (
    <>
      <JsonLd listing={listing} />
      <div className="max-w-3xl mx-auto px-4 py-12">
        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="text-sm text-gray-500 mb-6">
          <ol className="flex items-center gap-1.5 flex-wrap">
            <li><Link href="/" className="hover:text-primary-600">Home</Link></li>
            <li aria-hidden="true">›</li>
            <li>
              <Link href={`/${stateSlug}`} className="hover:text-primary-600">
                {listing.state}
              </Link>
            </li>
            <li aria-hidden="true">›</li>
            <li>
              <Link href={`/${stateSlug}/${citySlug}`} className="hover:text-primary-600">
                {listing.city}
              </Link>
            </li>
            <li aria-hidden="true">›</li>
            <li aria-current="page" className="text-gray-900 font-medium truncate max-w-[180px]">
              {listing.name}
            </li>
          </ol>
        </nav>

        {/* Header */}
        <header className="mb-8">
          <div className="flex items-start gap-3 flex-wrap mb-2">
            <h1 className="text-3xl font-bold text-gray-900 leading-tight">{listing.name}</h1>
            <TierBadge tier={listing.tier} />
          </div>
          <p className="text-gray-600">
            {listing.address || `${listing.city}, ${listing.state}`}
          </p>

          {/* Rating row */}
          {listing.rating !== null && (
            <div className="flex items-center gap-3 mt-3 text-sm">
              <span
                className="text-yellow-500 font-bold text-lg"
                aria-label={`Rating: ${listing.rating} out of 5`}
              >
                ★ {listing.rating.toFixed(1)}
              </span>
              {listing.reviews > 0 && (
                <span className="text-gray-500">({listing.reviews} reviews)</span>
              )}
            </div>
          )}

          {/* Badges row */}
          <div className="flex flex-wrap gap-2 mt-3">
            {listing.caps_certified && (
              <span className="bg-primary-50 text-primary-700 border border-primary-200 text-sm px-3 py-1 rounded-full font-medium">
                CAPS Certified
              </span>
            )}
            {listing.insured && (
              <span className="bg-green-50 text-green-700 border border-green-200 text-sm px-3 py-1 rounded-full">
                Licensed &amp; Insured
              </span>
            )}
            {listing.free_consultation && (
              <span className="bg-yellow-50 text-yellow-700 border border-yellow-200 text-sm px-3 py-1 rounded-full">
                Free Consultation
              </span>
            )}
            {listing.service_radius_miles !== null && (
              <span className="bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full">
                Serves up to {listing.service_radius_miles} miles
              </span>
            )}
          </div>
        </header>

        {/* Services */}
        {listing.services.length > 0 && (
          <section className="mb-8" aria-labelledby="services-heading">
            <h2 id="services-heading" className="text-lg font-bold text-gray-900 mb-3">
              Services Offered
            </h2>
            <ul className="flex flex-wrap gap-2" aria-label="Accessibility services">
              {listing.services.map(s => (
                <li
                  key={s}
                  className="bg-primary-50 text-primary-800 border border-primary-200 px-3 py-1.5 rounded-lg text-sm font-medium"
                >
                  {SERVICE_LABELS[s] ?? s}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Contact / CTA */}
        <section className="bg-gray-50 border border-gray-200 rounded-xl p-6 mb-8">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Contact This Contractor</h2>
          <div className="flex flex-col sm:flex-row gap-3">
            {listing.phone && (
              <a
                href={`tel:${listing.phone}`}
                className="flex-1 flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-semibold px-5 py-3 rounded-lg transition-colors text-base"
                aria-label={`Call ${listing.name}: ${listing.phone}`}
              >
                📞 {listing.phone}
              </a>
            )}
            {isVerified && listing.website && (
              <a
                href={listing.website}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 bg-white border-2 border-primary-600 text-primary-700 hover:bg-primary-50 font-semibold px-5 py-3 rounded-lg transition-colors text-base"
                aria-label={`Visit ${listing.name} website`}
              >
                🌐 Visit Website
              </a>
            )}
          </div>
        </section>

        {/* Claim CTA for unverified */}
        {!isVerified && (
          <section className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-8">
            <h2 className="text-base font-bold text-yellow-800 mb-1">Is this your business?</h2>
            <p className="text-sm text-yellow-700 mb-3">
              Claim this listing to add your services, verify your credentials, and start
              receiving direct leads from AccessRemodel.
            </p>
            <Link
              href={`/claim?listing=${encodeURIComponent(listing.id)}`}
              className="inline-block bg-yellow-600 hover:bg-yellow-700 text-white font-semibold px-5 py-2.5 rounded-lg text-sm transition-colors"
            >
              Claim This Listing →
            </Link>
          </section>
        )}

        {/* Details table */}
        <section aria-labelledby="details-heading">
          <h2 id="details-heading" className="text-lg font-bold text-gray-900 mb-3">
            Business Details
          </h2>
          <dl className="divide-y divide-gray-200 border border-gray-200 rounded-xl overflow-hidden text-sm">
            {[
              { label: 'City', value: listing.city },
              { label: 'State', value: listing.state },
              listing.postal_code ? { label: 'ZIP Code', value: listing.postal_code } : null,
              listing.phone ? { label: 'Phone', value: listing.phone } : null,
              listing.website
                ? {
                    label: 'Website',
                    value: (
                      <a
                        href={listing.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:underline break-all"
                      >
                        {listing.website}
                      </a>
                    ),
                  }
                : null,
              { label: 'Verification Tier', value: <TierBadge tier={listing.tier} /> },
            ]
              .filter(Boolean)
              .map((item, i) => (
                <div key={i} className="grid grid-cols-2 px-4 py-3 bg-white even:bg-gray-50">
                  <dt className="font-medium text-gray-700">{item!.label}</dt>
                  <dd className="text-gray-900">{item!.value}</dd>
                </div>
              ))}
          </dl>
        </section>
      </div>
    </>
  )
}
