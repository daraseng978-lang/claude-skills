# Site Config — accessremodel.co

Pre-filled values for the Next.js app scaffold tomorrow. Copy into the corresponding files when you generate the site.

## Brand

- **Name:** AccessRemodel
- **Tagline:** Find ADA-accessible bathroom contractors near you
- **Domain:** `accessremodel.co`
- **Canonical base URL:** `https://accessremodel.co`
- **Email sender:** `hello@accessremodel.co` (via Resend)

## `next.config.js` / env

```js
module.exports = {
  env: {
    NEXT_PUBLIC_SITE_URL: "https://accessremodel.co",
    NEXT_PUBLIC_SITE_NAME: "AccessRemodel",
  },
};
```

## Root metadata (`app/layout.tsx`)

```tsx
export const metadata = {
  metadataBase: new URL("https://accessremodel.co"),
  title: {
    default: "AccessRemodel — ADA-Accessible Bathroom Contractors Near You",
    template: "%s | AccessRemodel",
  },
  description:
    "Find vetted ADA-accessible bathroom contractors in your area. Compare services, certifications, and service areas. Free quotes.",
  openGraph: {
    siteName: "AccessRemodel",
    type: "website",
    url: "https://accessremodel.co",
  },
  twitter: { card: "summary_large_image" },
  alternates: { canonical: "/" },
};
```

## `robots.txt` (`public/robots.txt`)

```
User-agent: *
Allow: /

Sitemap: https://accessremodel.co/sitemap.xml
```

## `sitemap.ts` (`app/sitemap.ts`) — skeleton

```ts
import type { MetadataRoute } from "next";
import listings from "@/data/listings.json";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://accessremodel.co";
  const staticPages = ["", "/about", "/how-it-works", "/for-contractors"];
  const listingPages = listings.map((l: any) => ({
    url: `${base}/contractor/${l.id}`,
    lastModified: new Date(),
    changeFrequency: "monthly" as const,
  }));
  return [
    ...staticPages.map((p) => ({ url: `${base}${p}`, changeFrequency: "weekly" as const })),
    ...listingPages,
  ];
}
```

## DNS records (set at registrar)

| Type | Name | Value | TTL |
|---|---|---|---|
| A | @ | 76.76.21.21 | 3600 |
| CNAME | www | cname.vercel-dns.com | 3600 |
| TXT | @ | (Resend verification string) | 3600 |
| MX | send | feedback-smtp.us-east-1.amazonses.com (priority 10) | 3600 |
| TXT | send | v=spf1 include:amazonses.com ~all | 3600 |
| TXT | resend._domainkey | (Resend DKIM string) | 3600 |

## Schema.org JSON-LD (inject per listing page)

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "{{listing.name}}",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "{{listing.address}}",
    "addressLocality": "{{listing.city}}",
    "addressRegion": "{{listing.state}}",
    "postalCode": "{{listing.postal_code}}"
  },
  "telephone": "{{listing.phone}}",
  "url": "{{listing.website}}",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{listing.rating}}",
    "reviewCount": "{{listing.reviews}}"
  },
  "knowsAbout": ["ADA compliance", "aging-in-place remodeling", "accessible bathroom design"]
}
```

## Lead form → Resend payload

```ts
// app/api/lead/route.ts
import { Resend } from "resend";
const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(req: Request) {
  const { name, phone, zip, service, contractorId } = await req.json();
  await resend.emails.send({
    from: "leads@accessremodel.co",
    to: "founder@accessremodel.co", // change to your inbox
    subject: `New lead: ${service} in ${zip}`,
    text: `Name: ${name}\nPhone: ${phone}\nZIP: ${zip}\nService: ${service}\nContractor: ${contractorId}`,
  });
  return Response.json({ ok: true });
}
```

## Google Search Console

After deploy:
1. https://search.google.com/search-console → Add property → **Domain** → `accessremodel.co`
2. Verify via TXT record at registrar
3. Submit `https://accessremodel.co/sitemap.xml`
