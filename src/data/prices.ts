/**
 * ─────────────────────────────────────────────────────────────
 *  ALL PRICES LIVE HERE. Change a number once and every page,
 *  pricing card, comparison table and "You save" badge updates.
 *  Amounts are whole US dollars.
 *
 *  Plan names, descriptions and feature lists are in
 *  src/data/en/pricing.ts (text that will be translated later).
 * ─────────────────────────────────────────────────────────────
 */

/** Website projects — one-time, "starting at" prices. */
export const websitePrices = {
  landing: 950,
  essential: 2500,
  professional: 4500,
  premium: 7500,
  ecommerce: 5000,
} as const;

/** One-time setup fees. */
export const setupFees = {
  localSeo: 600,
  social: 250,
} as const;

/** Monthly plans (per month). */
export const monthlyPrices = {
  // Website Care
  careBasic: 79,
  careStandard: 149,
  carePro: 349,
  // Local SEO
  seoGbp: 175,
  seoStart: 450,
  seoGrowth: 950,
  // Social Media
  socialStart: 550,
  socialPlus: 950,
  socialPro: 1500,
} as const;

export type MonthlyPlanId = keyof typeof monthlyPrices;

/** Minimum commitment in months. */
export const minimumTerms = {
  localSeo: 6,
  social: 3,
} as const;

/**
 * Bundles: monthly price + the plans included.
 * "You save" is calculated automatically from the plans above.
 */
export const bundles = [
  { id: 'essential', price: 529, includes: ['careStandard', 'seoStart'] },
  { id: 'presence', price: 990, includes: ['careStandard', 'seoStart', 'socialStart'], popular: true },
  { id: 'growth', price: 1790, includes: ['careStandard', 'seoGrowth', 'socialPlus'] },
  { id: 'complete', price: 2450, includes: ['carePro', 'seoGrowth', 'socialPro'] },
] as const satisfies ReadonlyArray<{
  id: string;
  price: number;
  includes: readonly MonthlyPlanId[];
  popular?: boolean;
}>;

export type BundleId = (typeof bundles)[number]['id'];

/** Sum of the included plans if bought one by one. */
export const separateTotal = (includes: readonly MonthlyPlanId[]) =>
  includes.reduce((sum, id) => sum + monthlyPrices[id], 0);

export const bundleSavings = (b: (typeof bundles)[number]) => separateTotal(b.includes) - b.price;

/** Format a whole-dollar amount: 2500 → "$2,500". */
export const usd = (n: number) => `$${n.toLocaleString('en-US')}`;

/** Lowest monthly price for "starting at" teasers. */
export const lowest = {
  website: Math.min(...Object.values(websitePrices)),
  seo: Math.min(monthlyPrices.seoGbp, monthlyPrices.seoStart, monthlyPrices.seoGrowth),
  social: Math.min(monthlyPrices.socialStart, monthlyPrices.socialPlus, monthlyPrices.socialPro),
  bundle: Math.min(...bundles.map((b) => b.price)),
};
