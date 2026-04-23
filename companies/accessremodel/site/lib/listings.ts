import listingsRaw from '../data/listings.json'

export type Tier = 'specialist' | 'offers' | 'unverified'

export interface Listing {
  id: string
  name: string
  slug: string
  address: string
  city: string
  state: string
  postal_code: string
  phone: string
  website: string
  rating: number | null
  reviews: number
  lat: number | null
  lng: number | null
  tier: Tier
  verdict: string
  confidence: number
  services: string[]
  caps_certified: boolean
  insured: boolean
  service_radius_miles: number | null
  free_consultation: boolean
}

export const listings = listingsRaw as Listing[]

export function slugify(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export const SERVICE_LABELS: Record<string, string> = {
  grab_bars: 'Grab Bars',
  roll_in_shower: 'Roll-In Shower',
  walk_in_tub: 'Walk-In Tub',
  curbless_shower: 'Curbless Shower',
  accessible_vanity: 'Accessible Vanity',
  raised_toilet: 'Raised Toilet',
  shower_seat: 'Shower Seat',
  non_slip_flooring: 'Non-Slip Flooring',
  stair_lift: 'Stair Lift',
  ramp_install: 'Ramp Installation',
  widened_doorways: 'Widened Doorways',
}

export interface StateInfo {
  name: string
  slug: string
  count: number
}

export interface CityInfo {
  name: string
  slug: string
  count: number
}

export function getStates(): StateInfo[] {
  const map = new Map<string, number>()
  for (const l of listings) {
    map.set(l.state, (map.get(l.state) ?? 0) + 1)
  }
  return Array.from(map.entries())
    .map(([name, count]) => ({ name, slug: slugify(name), count }))
    .sort((a, b) => b.count - a.count)
}

export function getStateBySlug(slug: string): string | undefined {
  return listings.find(l => slugify(l.state) === slug)?.state
}

export function getCitiesForState(stateSlug: string): CityInfo[] {
  const state = getStateBySlug(stateSlug)
  if (!state) return []
  const map = new Map<string, number>()
  for (const l of listings.filter(l => l.state === state)) {
    map.set(l.city, (map.get(l.city) ?? 0) + 1)
  }
  return Array.from(map.entries())
    .map(([name, count]) => ({ name, slug: slugify(name), count }))
    .sort((a, b) => b.count - a.count)
}

export function getListingsForState(stateSlug: string): Listing[] {
  const state = getStateBySlug(stateSlug)
  if (!state) return []
  return listings.filter(l => l.state === state)
}

export function getListingsForCity(stateSlug: string, citySlug: string): Listing[] {
  const state = getStateBySlug(stateSlug)
  if (!state) return []
  return listings.filter(
    l => l.state === state && slugify(l.city) === citySlug,
  )
}

export function getListingById(id: string): Listing | undefined {
  return listings.find(l => l.id === id)
}

export const TIER_ORDER: Tier[] = ['specialist', 'offers', 'unverified']
