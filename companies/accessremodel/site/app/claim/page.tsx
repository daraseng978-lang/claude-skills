import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Claim Your Listing',
  description:
    'Is your contracting business listed on AccessRemodel? Claim and verify your listing to unlock enhanced visibility and direct leads.',
}

export default function ClaimPage() {
  const mailtoHref =
    'mailto:listings@accessremodel.com?subject=Claim%20My%20Listing&body=Business%20name%3A%0ABusiness%20website%3A%0APhone%3A%0AMessage%3A'

  return (
    <div className="max-w-xl mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold text-gray-900 mb-3">Claim Your Listing</h1>
      <p className="text-gray-600 mb-8">
        If your business is in our directory, you can claim it to update your information,
        add services, and receive verified-contractor status. Fill out the form below — we
        respond within 1 business day.
      </p>

      <form
        action={mailtoHref}
        method="GET"
        className="flex flex-col gap-5"
        aria-label="Claim listing form"
      >
        <div className="flex flex-col gap-1.5">
          <label htmlFor="biz-name" className="text-sm font-medium text-gray-700">
            Business Name <span aria-hidden="true">*</span>
          </label>
          <input
            id="biz-name"
            name="biz-name"
            type="text"
            required
            placeholder="Your business name"
            className="border border-gray-300 rounded-lg px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-600"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="website" className="text-sm font-medium text-gray-700">
            Website
          </label>
          <input
            id="website"
            name="website"
            type="url"
            placeholder="https://yourbusiness.com"
            className="border border-gray-300 rounded-lg px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-600"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="phone" className="text-sm font-medium text-gray-700">
            Phone
          </label>
          <input
            id="phone"
            name="phone"
            type="tel"
            placeholder="+1 (555) 000-0000"
            className="border border-gray-300 rounded-lg px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-600"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="email" className="text-sm font-medium text-gray-700">
            Your Email <span aria-hidden="true">*</span>
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            placeholder="you@yourbusiness.com"
            className="border border-gray-300 rounded-lg px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-600"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="message" className="text-sm font-medium text-gray-700">
            Message
          </label>
          <textarea
            id="message"
            name="message"
            rows={4}
            placeholder="Any additional details about your business or the listing…"
            className="border border-gray-300 rounded-lg px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-600 resize-y"
          />
        </div>

        <button
          type="submit"
          className="bg-primary-600 hover:bg-primary-700 text-white font-semibold text-base px-6 py-3 rounded-lg transition-colors mt-2"
        >
          Submit Claim Request
        </button>

        <p className="text-xs text-gray-400">
          Submitting opens your email client. Alternatively, email{' '}
          <a
            href="mailto:listings@accessremodel.com"
            className="text-primary-600 hover:underline"
          >
            listings@accessremodel.com
          </a>{' '}
          directly.
        </p>
      </form>
    </div>
  )
}
