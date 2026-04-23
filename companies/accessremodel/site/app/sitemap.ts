import type { MetadataRoute } from 'next'
import { listings, getStates, getCitiesForState } from '@/lib/listings'

const BASE = 'https://accessremodel.com'

export default function sitemap(): MetadataRoute.Sitemap {
  const routes: MetadataRoute.Sitemap = [
    { url: BASE, changeFrequency: 'weekly', priority: 1 },
    { url: `${BASE}/claim`, changeFrequency: 'yearly', priority: 0.3 },
  ]

  for (const state of getStates()) {
    routes.push({
      url: `${BASE}/${state.slug}`,
      changeFrequency: 'weekly',
      priority: 0.8,
    })
    for (const city of getCitiesForState(state.slug)) {
      routes.push({
        url: `${BASE}/${state.slug}/${city.slug}`,
        changeFrequency: 'weekly',
        priority: 0.7,
      })
    }
  }

  for (const listing of listings) {
    routes.push({
      url: `${BASE}/listing/${listing.id}`,
      changeFrequency: 'monthly',
      priority: 0.6,
    })
  }

  return routes
}
