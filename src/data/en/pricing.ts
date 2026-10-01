/**
 * Plan names, descriptions and feature lists (English).
 * PRICES ARE NOT HERE — edit them in src/data/prices.ts.
 *
 * Lines marked "REVIEW" are reasonable defaults written for you;
 * confirm they match what you actually deliver.
 */
import {
  bundles,
  minimumTerms,
  monthlyPrices,
  setupFees,
  websitePrices,
  type BundleId,
  type MonthlyPlanId,
} from '../prices';

export type Feature = string;

/* ───────────────────────── Website projects ───────────────────────── */

export interface WebsiteTier {
  id: keyof typeof websitePrices;
  name: string;
  pages: string;
  timeline: string;
  bestFor: string;
  features: Feature[];
  highlight?: boolean;
}

export const websiteTiers: WebsiteTier[] = [
  {
    id: 'landing',
    name: 'Landing Page',
    pages: '1 page',
    timeline: 'About 1 week',
    bestFor: 'A single offer, a new business, or an ad campaign that needs one clear page.',
    features: [
      'One focused, mobile-ready page',
      'Contact form that sends leads to your inbox',
      'Basic SEO setup (titles, descriptions, headings)',
      'Google Analytics + Search Console connected',
    ],
  },
  {
    id: 'essential',
    name: 'Essential Website',
    pages: 'Up to 5 pages',
    timeline: '2–3 weeks',
    bestFor: 'Small businesses that need a professional site that looks good and gets calls.',
    features: [
      'Up to 5 pages (Home, About, Services, Contact and one more)',
      'Design customized to your brand',
      'On-page SEO for every page',
      '2 rounds of revisions',
      '30 days of post-launch support',
    ],
  },
  {
    id: 'professional',
    name: 'Professional Website',
    pages: '6–10 pages',
    timeline: '4–6 weeks',
    bestFor: 'Established businesses with several services that want to rank for each one.',
    highlight: true,
    features: [
      '6–10 pages with a custom-designed homepage',
      'A dedicated page for each service',
      'Portfolio / project gallery',
      'Blog, ready for SEO content',
      'Google reviews displayed on your site',
      'Quote request form',
      'Schema markup for richer Google results',
      '3 rounds of revisions',
    ],
  },
  {
    id: 'premium',
    name: 'Premium Website',
    pages: '11–20 pages',
    timeline: '6–8 weeks',
    bestFor: 'Businesses serving several cities or offering many services that want to win them all.',
    features: [
      '11–20 pages with a fully custom design',
      'City / service-area pages to rank in each market',
      'Booking or CRM integration',
      'Copywriting included — we write every page',
      'Everything in Professional',
    ],
  },
  {
    id: 'ecommerce',
    name: 'E-commerce',
    pages: 'Up to 50 products',
    timeline: 'Quoted per project',
    bestFor: 'Selling products online with a store you can manage yourself.',
    features: [
      'Shopify or WooCommerce store',
      'Up to 50 products loaded and organized',
      'Payments, shipping and taxes set up',
      'Mobile-first product and checkout pages',
      'On-page SEO for products and categories',
    ],
  },
];

export const websiteAddOns: string[] = [
  'Logo design',
  'Full brand identity (colors, fonts, guidelines)',
  'Professional copywriting',
  'Extra pages',
  'Photography direction',
  'Content migration from your old site',
];

/* ───────────────────────── Monthly plans ───────────────────────── */

export interface MonthlyPlan {
  id: MonthlyPlanId;
  name: string;
  short: string;
  summary: string;
  features: Feature[];
  /** Values used by the comparison table. */
  specs: Record<string, string>;
  highlight?: boolean;
  note?: string;
}

export const carePlans: MonthlyPlan[] = [
  {
    id: 'careBasic',
    name: 'Website Care Basic',
    short: 'Basic',
    summary: 'Keep your site safe, fast and online.',
    // REVIEW: confirm what Basic includes
    features: [
      'Hosting management + SSL certificate',
      'Software and security updates',
      'Weekly backups',
      'Uptime monitoring',
      'Edits billed by the hour when you need them',
    ],
    specs: { edits: 'Billed hourly', support: 'Email' },
  },
  {
    id: 'careStandard',
    name: 'Website Care Standard',
    short: 'Standard',
    summary: 'Everything in Basic, plus an hour of edits every month.',
    highlight: true,
    features: [
      'Everything in Basic',
      '1 hour of edits per month',
      'Daily backups', // REVIEW
      'Monthly speed and health check', // REVIEW
    ],
    specs: { edits: '1 hr / month', support: 'Email + phone' },
  },
  {
    id: 'carePro',
    name: 'Website Care Pro',
    short: 'Pro',
    summary: 'For businesses that update their site often.',
    features: [
      'Everything in Standard',
      '3 hours of edits per month',
      'Priority support (next business day)', // REVIEW
      'Quarterly conversion review', // REVIEW
    ],
    specs: { edits: '3 hrs / month', support: 'Priority' },
  },
];

export const seoSetup = {
  name: 'Local SEO Setup',
  price: setupFees.localSeo,
  summary: 'A one-time project that fixes the foundation, so monthly work actually moves the needle.',
  features: [
    'Full SEO audit of your website and Google presence',
    'Google Business Profile optimization',
    'Google Search Console + Analytics setup',
    'Keyword research for your services and service area',
    'On-page SEO for up to 10 pages',
    'LocalBusiness schema markup',
    'Listings on 30 local directories',
  ],
};

export const seoPlans: MonthlyPlan[] = [
  {
    id: 'seoGbp',
    name: 'Google Profile Only',
    short: 'Google Profile',
    summary: 'Keep your Google Business Profile active, accurate and attractive.',
    // REVIEW: confirm monthly deliverables
    features: [
      '4 Google Business Profile posts per month',
      'Photo uploads and profile updates',
      'Review monitoring and reply drafts',
      'Q&A and listing accuracy checks',
      'Monthly Google profile report',
    ],
    specs: { keywords: '—', content: 'GBP posts only' },
  },
  {
    id: 'seoStart',
    name: 'Local SEO Start',
    short: 'SEO Start',
    summary: 'Steady monthly work to climb the local map pack and organic results.',
    // REVIEW: confirm monthly deliverables
    features: [
      'Everything in Google Profile Only',
      'Ongoing on-page SEO improvements',
      'New directory citations and cleanup every month',
      'Simple review-request system for your customers',
      'Rank tracking for up to 15 keywords',
      'Plain-English monthly report',
    ],
    specs: { keywords: 'Up to 15', content: 'On-page updates' },
  },
  {
    id: 'seoGrowth',
    name: 'Local SEO Growth',
    short: 'SEO Growth',
    summary: 'For competitive markets, or businesses targeting several cities.',
    highlight: true,
    // REVIEW: confirm monthly deliverables
    features: [
      'Everything in Local SEO Start',
      '2 SEO articles or new service/city pages per month',
      'Local link building',
      'Rank tracking for up to 40 keywords',
      'Competitor tracking',
      'Monthly strategy call',
    ],
    specs: { keywords: 'Up to 40', content: '2 pages or articles / month' },
  },
];

export const socialSetup = {
  name: 'Social Media Setup',
  price: setupFees.social,
  summary: 'We get your profiles ready before the first post goes out.',
  features: [
    'Profile optimization (bio, links, highlights, cover images)',
    'Branded post and story templates',
    'Your first content calendar',
  ],
};

export const socialPlans: MonthlyPlan[] = [
  {
    id: 'socialStart',
    name: 'Social Start',
    short: 'Social Start',
    summary: 'A consistent, professional presence without you lifting a finger.',
    features: [
      '12 posts per month',
      'Instagram + Facebook',
      'Custom graphics and captions',
      'Monthly content calendar for your approval',
      'Monthly performance report',
    ],
    specs: {
      posts: '12',
      reels: '—',
      stories: '—',
      platforms: 'Instagram + Facebook',
      community: '—',
      session: '—',
      ads: '—',
    },
  },
  {
    id: 'socialPlus',
    name: 'Social Plus',
    short: 'Social Plus',
    summary: 'More video, more platforms and real conversations with your followers.',
    highlight: true,
    features: [
      '16 posts per month, including 4 Reels',
      '8 stories per month',
      'Up to 3 platforms',
      'Community management (comments and messages)',
      'Monthly performance report',
    ],
    specs: {
      posts: '16',
      reels: '4',
      stories: '8',
      platforms: 'Up to 3',
      community: 'Included',
      session: '—',
      ads: '—',
    },
  },
  {
    id: 'socialPro',
    name: 'Social Pro',
    short: 'Social Pro',
    summary: 'A full-service social team, including content shot at your business.',
    features: [
      '20 posts per month, including 8 Reels',
      '12 stories per month',
      'Daily community management',
      '1 on-site content session per month',
      'Ads management (ad spend billed separately)',
    ],
    // REVIEW: on-site sessions outside your local area — decide on travel fees
    note: 'Ad spend is paid directly to Meta/TikTok and billed separately. On-site sessions outside the Charleston, SC area may include travel costs.',
    specs: {
      posts: '20',
      reels: '8',
      stories: '12',
      platforms: 'Up to 3',
      community: 'Daily',
      session: '1 / month',
      ads: 'Included',
    },
  },
];

/* ───────────────────────── Bundles ───────────────────────── */

export const bundleText: Record<BundleId, { name: string; tagline: string; bestFor: string }> = {
  essential: {
    name: 'Essential',
    tagline: 'Get found on Google',
    bestFor: 'Businesses that want a well-kept website and steady local SEO.',
  },
  presence: {
    name: 'Presence',
    tagline: 'Found on Google, active on social',
    bestFor: 'Most small businesses: search, social and website handled in one plan.',
  },
  growth: {
    name: 'Growth',
    tagline: 'Win a competitive market',
    bestFor: 'Businesses ready to outrank competitors and build an audience.',
  },
  complete: {
    name: 'Complete',
    tagline: 'Your full marketing team',
    bestFor: 'Businesses that want everything done for them, including video and ads.',
  },
};

export const annualNote =
  '12-month plans: setup fees waived or website paid in 6 interest-free installments.';

export const termsNote = `Local SEO plans have a ${minimumTerms.localSeo}-month minimum. Social media plans have a ${minimumTerms.social}-month minimum. Bundles follow the longest minimum included.`;

/* ───────────────────────── Helpers ───────────────────────── */

export const allMonthlyPlans: MonthlyPlan[] = [...carePlans, ...seoPlans, ...socialPlans];

export const getPlan = (id: MonthlyPlanId) => {
  const plan = allMonthlyPlans.find((p) => p.id === id);
  if (!plan) throw new Error(`Unknown plan id: ${id}`);
  return { ...plan, price: monthlyPrices[id] };
};

const pick = (bundleId: BundleId, prefix: 'care' | 'seo' | 'social') => {
  const b = bundles.find((x) => x.id === bundleId)!;
  const id = (b.includes as readonly MonthlyPlanId[]).find((i) => i.startsWith(prefix));
  return id ? getPlan(id) : undefined;
};

/** Comparison table rows. A value of `true` shows a check, `false`/'—' shows a dash. */
export const comparisonRows: { group: string; label: string; value: (b: BundleId) => string | boolean }[] = [
  { group: 'Website', label: 'Website Care plan', value: (b) => pick(b, 'care')?.short ?? false },
  { group: 'Website', label: 'Hosting, updates and backups', value: () => true },
  { group: 'Website', label: 'Website edits included', value: (b) => pick(b, 'care')?.specs.edits ?? false },
  { group: 'Local SEO', label: 'Local SEO plan', value: (b) => pick(b, 'seo')?.short ?? false },
  { group: 'Local SEO', label: 'Google Business Profile management', value: () => true },
  { group: 'Local SEO', label: 'Keywords tracked', value: (b) => pick(b, 'seo')?.specs.keywords ?? false },
  { group: 'Local SEO', label: 'New SEO content', value: (b) => pick(b, 'seo')?.specs.content ?? false },
  { group: 'Social media', label: 'Social media plan', value: (b) => pick(b, 'social')?.short ?? false },
  { group: 'Social media', label: 'Posts per month', value: (b) => pick(b, 'social')?.specs.posts ?? false },
  { group: 'Social media', label: 'Reels per month', value: (b) => pick(b, 'social')?.specs.reels ?? false },
  { group: 'Social media', label: 'Stories per month', value: (b) => pick(b, 'social')?.specs.stories ?? false },
  { group: 'Social media', label: 'Platforms', value: (b) => pick(b, 'social')?.specs.platforms ?? false },
  { group: 'Social media', label: 'Community management', value: (b) => pick(b, 'social')?.specs.community ?? false },
  { group: 'Social media', label: 'On-site content session', value: (b) => pick(b, 'social')?.specs.session ?? false },
  { group: 'Social media', label: 'Ads management', value: (b) => pick(b, 'social')?.specs.ads ?? false },
  { group: 'Reporting', label: 'Monthly report', value: () => true },
];
