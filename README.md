# Braven Digital — Website

The marketing website for **Braven Digital**, a small-business marketing studio based in Goose Creek, SC, serving clients across the US.

Built with [Astro 5](https://astro.build) + [Tailwind CSS 4](https://tailwindcss.com). Fully static, almost no JavaScript, and Lighthouse 100 / 100 / 100 / 100 on mobile in local testing.

---

## Contents

1. [Quick start](#quick-start)
2. [Before you launch — checklist](#before-you-launch--checklist)
3. [Where everything lives](#where-everything-lives)
4. [Editing content](#editing-content)
5. [Changing prices](#changing-prices)
6. [Replacing placeholders](#replacing-placeholders)
7. [Connecting the contact form](#connecting-the-contact-form)
8. [Connecting Google Analytics 4](#connecting-google-analytics-4)
9. [Booking link (Calendly)](#booking-link-calendly)
10. [Writing blog posts](#writing-blog-posts)
11. [Deploying + custom domain](#deploying--custom-domain)
12. [After launch: Google setup](#after-launch-google-setup)
13. [Adding Portuguese and Spanish](#adding-portuguese-and-spanish)
14. [Design system](#design-system)
15. [SEO features](#seo-features)

---

## Quick start

You need [Node.js 20+](https://nodejs.org) (22 recommended).

```bash
npm install        # install dependencies (first time only)
npm run dev        # local preview at http://localhost:4321 — updates as you edit
npm run build      # production build into ./dist
npm run preview    # preview the production build
npm run check      # type-check the project
```

---

## Before you launch — checklist

Search the project for `PLACEHOLDER`, `[YOUR NAME]`, `[PHONE]`, `[EMAIL]`, `[CALENDLY LINK]`, `[INSTAGRAM URL]` and `REVIEW` — every one of them should be gone or confirmed.

- [ ] `src/config/site-url.mjs` — your real domain
- [ ] `src/config/site.ts` — founder name, phone (both formats), email, hours, booking link, Instagram, legal name
- [ ] `src/config/site.ts` — `formspreeId` (or switch to Netlify Forms) → [form setup](#connecting-the-contact-form)
- [ ] `src/config/site.ts` — `ga4Id` → [analytics setup](#connecting-google-analytics-4)
- [ ] `src/data/en/testimonials.ts` — real client quotes (or remove them)
- [ ] `src/data/en/portfolio.ts` + `src/assets/portfolio/` — real projects and images
- [ ] `src/pages/about.astro` + `src/assets/about/founder-placeholder.jpg` — your story and photo
- [ ] `src/assets/blog/*.jpg` — real blog cover images
- [ ] `src/data/en/pricing.ts` — confirm every line marked `REVIEW` matches what you deliver
- [ ] `src/data/en/faqs.ts` — confirm payment, cancellation and ownership answers match your contracts
- [ ] `src/pages/privacy.astro` + `src/pages/terms.astro` — have them reviewed; replace `[DATE]` and the `[bracketed]` tools
- [ ] `src/data/en/services.ts` — the "20-minute call" and "reply within one business day" promises are accurate

---

## Where everything lives

```
src/
├── config/
│   ├── site-url.mjs        ← your domain
│   └── site.ts             ← name, phone, email, links, GA4 ID, form ID
├── data/
│   ├── prices.ts           ← ★ EVERY PRICE (one place)
│   ├── blog-categories.ts  ← blog categories
│   ├── index.ts            ← loads content by language
│   └── en/                 ← English text content
│       ├── pricing.ts      ← plan names, descriptions, feature lists, comparison table
│       ├── services.ts     ← service summaries + "how it works" steps
│       ├── faqs.ts         ← all FAQs, grouped by page
│       ├── testimonials.ts ← testimonials (placeholders)
│       └── portfolio.ts    ← case studies (placeholders)
├── content/blog/en/        ← blog posts (Markdown / MDX)
├── assets/                 ← images (auto-optimized to AVIF/WebP)
├── i18n/ui.ts              ← button labels, nav labels, footer text
├── components/             ← reusable building blocks
├── layouts/                ← page shell (SEO tags, header, footer)
├── pages/                  ← one file per page (URL = file path)
└── styles/global.css       ← colors, fonts, buttons
public/                     ← logo SVGs, favicons, share image, _headers
```

**Rule of thumb:** to change *words or prices*, edit `src/data/` or `src/config/`. You should rarely need to touch `components/` or `layouts/`.

---

## Editing content

| What you want to change | File |
| --- | --- |
| Phone, email, hours, social links | `src/config/site.ts` |
| Service card text, process steps | `src/data/en/services.ts` |
| Plan names, features, "what's included" | `src/data/en/pricing.ts` |
| FAQ questions and answers | `src/data/en/faqs.ts` |
| Testimonials | `src/data/en/testimonials.ts` |
| Case studies | `src/data/en/portfolio.ts` |
| Buttons, menu labels, footer blurb | `src/i18n/ui.ts` |
| Page headlines and intro text | the page file in `src/pages/` (look for `title=` and `lead=`) |
| SEO title and meta description | top of each page file (`<BaseLayout title="…" description="…">`) |

FAQ answers can contain simple links, e.g. `'See our <a href="/pricing/">pricing</a>.'`.

---

## Changing prices

**All prices live in [`src/data/prices.ts`](src/data/prices.ts).** Change a number there and it updates everywhere: service pages, pricing cards, bundles, the comparison table, FAQ answers, structured data, meta descriptions and even the blog posts.

```ts
export const monthlyPrices = {
  careStandard: 149,   // ← change this…
  seoStart: 450,
  ...
};
export const bundles = [
  { id: 'essential', price: 529, includes: ['careStandard', 'seoStart'] },
  ...
];
```

- **"Save $X vs. buying separately"** is calculated automatically — never type it by hand.
- To change what a bundle contains, edit its `includes` list.
- To mark a different bundle as "Most Popular", move `popular: true`.
- Minimum terms (6 months SEO, 3 months social) are in `minimumTerms`.
- The 12-month offer text is `annualNote` in `src/data/en/pricing.ts`.

---

## Replacing placeholders

Placeholders show a yellow **PLACEHOLDER** tag on the site so they are impossible to miss.

### Testimonials — `src/data/en/testimonials.ts`
Replace the quote, name and role, then set `placeholder: false`. **Only use real quotes, with the client's permission.** To hide the section until you have some, delete the entries and remove `<Testimonials …/>` from `src/pages/index.astro` and `src/pages/work/index.astro`.

### Case studies — `src/data/en/portfolio.ts`
For each project:
1. Put a screenshot or photo (landscape, ~1600×1000) in `src/assets/portfolio/`, and update the `import` at the top of the file.
2. Change the `slug` to something descriptive (e.g. `roofing-company-website-charleston`). **Slugs starting with `placeholder-` are hidden from Google** (noindex + left out of the sitemap).
3. Fill in the client type, challenge, what you did and the results. Only real, verifiable results.
4. Set `placeholder: false`.

### Founder story and photo — `src/pages/about.astro`
Replace the bracketed text in the "Hi, I'm…" section and replace `src/assets/about/founder-placeholder.jpg` with a portrait (4:5 ratio, ~1000×1250). Keep the file name, or update the import.

### Logo
The wordmark is in `public/brand/` (dark and light versions, outlined SVG — no font needed) and used inline via `src/components/Logo.astro`. Favicons: `public/favicon.svg`, `favicon.ico`, `apple-touch-icon.png`, `icon-512.png`. The default social share image is `public/og-default.png` (1200×630).

---

## Connecting the contact form

The form at `/contact/` collects name, business name, email, phone, service, budget and message, with a hidden **honeypot** field to catch spam bots. After sending, visitors land on `/thank-you/`.

### Option A — Formspree (default, works on any host)
1. Create a free account at [formspree.io](https://formspree.io) and create a new form.
2. Copy the form ID from the endpoint — in `https://formspree.io/f/xyzabcde` it is `xyzabcde`.
3. In `src/config/site.ts` set `formspreeId: 'xyzabcde'` (and keep `formProvider: 'formspree'`).
4. Deploy, submit a test, and confirm the email in Formspree.

Formspree's `_gotcha` honeypot is already set up. The form submits in the background and redirects to `/thank-you/`; without JavaScript it still works (Formspree shows its own confirmation page).

### Option B — Netlify Forms (only if you host on Netlify)
1. In `src/config/site.ts` set `formProvider: 'netlify'`.
2. Deploy to Netlify. The form is detected automatically (look under **Forms** in your Netlify dashboard).
3. Set up email notifications under **Forms → Form notifications**.

---

## Connecting Google Analytics 4

1. In [Google Analytics](https://analytics.google.com), create a GA4 property and a **Web** data stream for your domain.
2. Copy the **Measurement ID** (looks like `G-XXXXXXXXXX`).
3. In `src/config/site.ts` set `ga4Id: 'G-XXXXXXXXXX'`.
4. Deploy. The tag only loads when an ID is present.

Recommended: in GA4, mark the `/thank-you/` page view as a **key event** (conversion) so you can count leads.

---

## Booking link (Calendly)

Set `bookingUrl` in `src/config/site.ts` (e.g. `https://calendly.com/your-name/free-call`). Every "Book a Free Call" button then links to it, and the `/contact/` page shows the calendar. To keep the page fast, the calendar only loads when a visitor clicks **Show available times**.

Until you set it, the booking buttons point to the contact page.

---

## Writing blog posts

Posts live in `src/content/blog/en/`. The file name becomes the URL:
`src/content/blog/en/roof-repair-costs.md` → `/blog/roof-repair-costs/`.

```md
---
title: 'Your Post Title (under 60 characters is ideal)'
description: 'A 140–160 character summary that appears in Google results.'
pubDate: 2026-11-15
updatedDate: 2026-12-01      # optional
category: local-seo          # web-design | local-seo | social-media
tags: ['google maps', 'reviews']
cover: '../../../assets/blog/your-image.jpg'
coverAlt: 'Describe the image for screen readers'
draft: false                 # true = hidden from the live site
---

Your content in Markdown. Use ## for main sections (they build the table of contents).
```

- `.md` files are plain Markdown. `.mdx` files can also pull in live prices (see the two starter posts: `{usd(websitePrices.landing)}`).
- Link to your service pages and other posts — internal links help SEO.
- Add categories in `src/data/blog-categories.ts`.
- Each post automatically gets BlogPosting schema, breadcrumbs, Open Graph tags, a sitemap entry and an RSS entry (`/rss.xml`).

---

## Deploying + custom domain

The site is fully static. The build command is `npm run build` and the output folder is `dist`.

**First, set your domain** in `src/config/site-url.mjs` (used for canonical URLs, the sitemap and social tags). Then push the project to a GitHub repository.

### Netlify
1. [app.netlify.com](https://app.netlify.com) → **Add new site → Import an existing project** → pick the repo. Settings are read from `netlify.toml`.
2. **Domain management → Add a domain** → enter `bravendigital.com`.
3. Either point your registrar's nameservers to Netlify DNS, or add the DNS records Netlify shows (an `A` record for the apex and a `CNAME` for `www`).
4. HTTPS is issued automatically. Set your preferred domain (with or without `www`) as primary.

### Vercel
1. [vercel.com/new](https://vercel.com/new) → import the repo. `vercel.json` sets everything up.
2. **Project → Settings → Domains** → add `bravendigital.com` and `www.bravendigital.com`.
3. Add the DNS records Vercel shows at your registrar. HTTPS is automatic.
4. Note: Netlify Forms do not work on Vercel — use Formspree.

### Cloudflare Pages
1. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git** → pick the repo.
2. Framework preset **Astro**, build command `npm run build`, output directory `dist`, and environment variable `NODE_VERSION = 22`.
3. **Custom domains → Set up a custom domain**. If your domain's DNS is on Cloudflare, records are added for you.
4. Note: use Formspree on Cloudflare Pages.

Security and caching headers are in `public/_headers` (Netlify + Cloudflare) and `vercel.json` (Vercel).

---

## After launch: Google setup

1. **Google Search Console** — add your domain, verify it, and submit `https://yourdomain.com/sitemap-index.xml`.
2. **Google Business Profile** — create or claim it as a *service-area business*. Use **exactly** the same name, phone and city as the website footer (NAP consistency).
3. **Bing Webmaster Tools** — import from Search Console in one click.
4. Test the structured data with [Google's Rich Results Test](https://search.google.com/test/rich-results).
5. Re-run Lighthouse on the live URL (Chrome DevTools → Lighthouse) or [PageSpeed Insights](https://pagespeed.web.dev).

---

## Adding Portuguese and Spanish

The project is already structured for this. English URLs stay as they are; new languages live under `/pt/` and `/es/`.

1. **Enable the locale** in `astro.config.mjs`: `locales: ['en', 'pt', 'es']`.
2. **Interface text** — in `src/i18n/ui.ts`, add `pt: 'Português'` to `languages` and a `pt: { … }` block with translated labels (missing keys fall back to English).
3. **Content** — copy `src/data/en/` to `src/data/pt/`, translate the text (prices stay in `prices.ts`, shared by all languages), and register it in `src/data/index.ts`.
4. **Pages** — create `src/pages/pt/` with the same files as `src/pages/`. Each page is short: it loads content with `getContent(lang)` and passes it to the shared components, so you mainly translate headlines and intro text. Update import paths (`../` → `../../`).
5. **Blog** — add translated posts in `src/content/blog/pt/` and a `src/pages/pt/blog/` route that calls `getPosts('pt')`.
6. **SEO** — add `hreflang` alternates in `src/layouts/BaseLayout.astro` (there is a comment marking the spot), set `<html lang>` from the current locale, and add a language switcher to the header.
7. Translate the URL slugs if you like (e.g. `/pt/criacao-de-sites/`) — good for local SEO in each language.

---

## Design system

**Palette — "Pine & Ember"** (defined in `src/styles/global.css` under `@theme`)

| Token | Hex | Use |
| --- | --- | --- |
| `pine` | `#1F4D45` | Main brand color: dark sections, links, icons |
| `ink` | `#16181D` | Body text |
| `ember` | `#C8461F` | Primary call-to-action buttons only (white text, 4.8:1 contrast) |
| `honey` | `#F2B33D` | Highlights on dark backgrounds, badges |
| `cream` | `#FBF6EE` | Page background |
| `sand` | `#EFE4D2` | Alternate section and card backgrounds |

Pine green and cream feel grounded and local, unlike the blue/purple "tech startup" look. Ember is used only on the main CTA buttons, so "Book a Free Call" is always the warmest thing on the page.

**Typography** — *Bricolage Grotesque* (headings) and *Figtree* (body), self-hosted via Fontsource, with full Latin character support for Portuguese and Spanish.

**Buttons** — `btn btn-primary` (ember), `btn btn-secondary` (outlined), `btn btn-light`, `btn btn-ghost-light` (for dark backgrounds).

**Animations** — sections fade up gently as they scroll into view (`data-reveal`). Disabled automatically for visitors who prefer reduced motion; content is fully visible without JavaScript.

---

## SEO features

- Unique `<title>` and meta description on every page, targeting small-business keywords
- One `<h1>` per page and a logical heading order
- JSON-LD structured data: `ProfessionalService` (every page), `WebSite`, `Service` + `OfferCatalog` (service pages), `FAQPage`, `BlogPosting`, `BreadcrumbList`
- Auto-generated `sitemap-index.xml` and `robots.txt`; `/rss.xml` for the blog
- Canonical URLs, Open Graph and Twitter cards (default share image + per-post images)
- Clean URLs with trailing slashes, breadcrumbs and internal links between related services and posts
- Images converted to AVIF/WebP at several sizes, lazy-loaded below the fold, width/height always set (no layout shift)
- NAP (name, area, phone, email) in the footer of every page
- Accessible: skip link, keyboard-friendly menus, visible focus, alt text, WCAG AA contrast, reduced-motion support
