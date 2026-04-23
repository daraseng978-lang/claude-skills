import Link from 'next/link'
import type { Listing } from '@/lib/listings'
import { SERVICE_LABELS } from '@/lib/listings'
import TierBadge from './TierBadge'

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="text-yellow-500 font-semibold text-sm" aria-label={`Rating: ${rating} out of 5`}>
      ★ {rating.toFixed(1)}
    </span>
  )
}

export default function ListingCard({ listing }: { listing: Listing }) {
  return (
    <article className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <Link
          href={`/listing/${listing.id}`}
          className="text-base font-semibold text-gray-900 hover:text-primary-700 leading-tight"
        >
          {listing.name}
        </Link>
        <TierBadge tier={listing.tier} />
      </div>

      <p className="text-sm text-gray-500">
        {listing.city}, {listing.state}
        {listing.postal_code ? ` ${listing.postal_code}` : ''}
      </p>

      <div className="flex items-center gap-3 text-sm">
        {listing.rating !== null && <StarRating rating={listing.rating} />}
        {listing.reviews > 0 && (
          <span className="text-gray-400">({listing.reviews} reviews)</span>
        )}
        {listing.caps_certified && (
          <span className="text-xs bg-primary-50 text-primary-700 border border-primary-200 px-2 py-0.5 rounded-full font-medium">
            CAPS Certified
          </span>
        )}
      </div>

      {listing.services.length > 0 && (
        <ul className="flex flex-wrap gap-1.5" aria-label="Services offered">
          {listing.services.slice(0, 4).map(s => (
            <li
              key={s}
              className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full"
            >
              {SERVICE_LABELS[s] ?? s}
            </li>
          ))}
          {listing.services.length > 4 && (
            <li className="text-xs text-gray-400">+{listing.services.length - 4} more</li>
          )}
        </ul>
      )}

      <div className="flex items-center gap-3 mt-auto pt-2 border-t border-gray-100 text-sm">
        {listing.phone && (
          <a
            href={`tel:${listing.phone}`}
            className="text-primary-600 hover:text-primary-800 font-medium"
            aria-label={`Call ${listing.name}`}
          >
            {listing.phone}
          </a>
        )}
        <Link
          href={`/listing/${listing.id}`}
          className="ml-auto text-primary-600 hover:text-primary-800 font-medium text-sm"
        >
          View details →
        </Link>
      </div>
    </article>
  )
}
