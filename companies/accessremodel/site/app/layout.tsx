import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'

const inter = Inter({ subsets: ['latin'], display: 'swap' })

export const metadata: Metadata = {
  metadataBase: new URL('https://accessremodel.com'),
  title: {
    default: 'AccessRemodel — ADA Bathroom Contractors Directory',
    template: '%s | AccessRemodel',
  },
  description:
    '247 vetted contractors across 11 states specializing in aging-in-place bathroom remodeling, grab bars, roll-in showers, and walk-in tubs.',
  openGraph: {
    title: 'AccessRemodel — ADA Bathroom Contractors',
    description:
      'Find ADA-accessible bathroom contractors near you. 247 specialists across 11 states.',
    type: 'website',
    url: 'https://accessremodel.com',
    siteName: 'AccessRemodel',
    images: [{ url: '/og-default.png', width: 1200, height: 630 }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AccessRemodel — ADA Bathroom Contractors',
    description: 'Find ADA-accessible bathroom contractors near you.',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} bg-gray-50 text-gray-900 antialiased`}>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 bg-primary-600 text-white px-4 py-2 rounded z-50"
        >
          Skip to main content
        </a>

        <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <Link
              href="/"
              className="text-xl font-bold text-primary-700 hover:text-primary-800"
              aria-label="AccessRemodel home"
            >
              AccessRemodel
            </Link>
            <nav aria-label="Main navigation">
              <ul className="flex items-center gap-6 text-sm font-medium text-gray-600">
                <li>
                  <Link href="/" className="hover:text-primary-700 transition-colors">
                    Home
                  </Link>
                </li>
                <li>
                  <Link
                    href="/claim"
                    className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    Claim Listing
                  </Link>
                </li>
              </ul>
            </nav>
          </div>
        </header>

        <main id="main" tabIndex={-1}>
          {children}
        </main>

        <footer className="bg-gray-900 text-gray-400 mt-20 py-12 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              <div>
                <p className="text-white font-bold text-lg mb-2">AccessRemodel</p>
                <p className="text-sm leading-relaxed">
                  The independent directory for ADA-accessible bathroom contractors.
                </p>
              </div>
              <div>
                <p className="text-white font-semibold mb-2">Quick Links</p>
                <ul className="space-y-1 text-sm">
                  <li><Link href="/" className="hover:text-white transition-colors">Home</Link></li>
                  <li><Link href="/claim" className="hover:text-white transition-colors">Claim Your Listing</Link></li>
                </ul>
              </div>
              <div>
                <p className="text-white font-semibold mb-2">For Contractors</p>
                <ul className="space-y-1 text-sm">
                  <li><Link href="/claim" className="hover:text-white transition-colors">Claim & Verify Your Listing</Link></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-800 pt-6 text-xs text-gray-500 leading-relaxed">
              <p>
                AccessRemodel is an independent directory. We earn referral fees on leads sent to
                partner contractors. Listing accuracy is not guaranteed — verify credentials
                independently before hiring.
              </p>
              <p className="mt-2">© {new Date().getFullYear()} AccessRemodel. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
