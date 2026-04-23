import SearchBar from './SearchBar'
import type { StateInfo } from '@/lib/listings'

export default function Hero({ states }: { states: StateInfo[] }) {
  return (
    <section
      className="bg-gradient-to-br from-primary-800 to-primary-600 text-white py-20 px-4"
      aria-labelledby="hero-heading"
    >
      <div className="max-w-3xl mx-auto text-center flex flex-col items-center gap-6">
        <h1 id="hero-heading" className="text-4xl md:text-5xl font-bold leading-tight">
          Find ADA-Accessible Bathroom Contractors Near You
        </h1>
        <p className="text-xl text-primary-100 max-w-2xl">
          247 vetted contractors across 11 states specializing in aging-in-place, roll-in
          showers, grab bars, and walk-in tubs.
        </p>
        <SearchBar states={states} />
        <p className="text-sm text-primary-200">
          Or browse by state below
        </p>
      </div>
    </section>
  )
}
