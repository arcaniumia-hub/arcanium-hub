/**
 * ─────────────────────────────────────────────────────────────
 *  BRAVEN DIGITAL — SITE SETTINGS
 *  Edit the values below. Everything marked [PLACEHOLDER] must be
 *  replaced before launch (search the project for "PLACEHOLDER").
 * ─────────────────────────────────────────────────────────────
 */
import { SITE_URL } from './site-url.mjs';

export const site = {
  name: 'Braven Digital',
  legalName: 'Braven Digital', // [PLACEHOLDER] e.g. "Braven Digital LLC"
  url: SITE_URL,
  tagline: 'Websites, Local SEO & Social Media for small businesses',
  description:
    'Braven Digital is a small-business marketing studio. We build fast websites, get you found on Google, and run your social media at fair, published prices.',

  founder: '[YOUR NAME]', // [PLACEHOLDER]

  // Contact — keep these identical everywhere (NAP consistency matters for SEO)
  phone: '[PHONE]', // [PLACEHOLDER] display format, e.g. "(843) 555-0123"
  phoneE164: '', // [PLACEHOLDER] for tel: links, e.g. "+18435550123"
  email: '[EMAIL]', // [PLACEHOLDER] e.g. "hello@bravendigital.com"

  address: {
    locality: 'Goose Creek',
    region: 'SC',
    regionName: 'South Carolina',
    postalCode: '29445',
    country: 'US',
  },
  serviceArea: 'Serving small businesses across the United States',
  serviceAreaShort: 'Nationwide (US)',
  languages: ['English', 'Português', 'Español'],
  hours: 'Mon–Fri, 9am–6pm ET', // [PLACEHOLDER] adjust to your real hours

  // Links
  bookingUrl: '[CALENDLY LINK]', // [PLACEHOLDER] e.g. "https://calendly.com/braven/free-call"
  social: {
    instagram: '[INSTAGRAM URL]', // [PLACEHOLDER]
    facebook: '', // optional
    linkedin: '', // optional
    tiktok: '', // optional
  },

  // Integrations
  ga4Id: '', // [PLACEHOLDER] e.g. "G-XXXXXXXXXX" — leave empty to disable Analytics
  formspreeId: '', // [PLACEHOLDER] e.g. "xyzabcde" from https://formspree.io/f/xyzabcde
  formProvider: 'formspree' as 'formspree' | 'netlify',

  ogImage: '/og-default.png',
  themeColor: '#1F4D45',
} as const;

/** True when a value is still an unreplaced placeholder like "[PHONE]". */
export const isPlaceholder = (v: string | undefined | null) => !v || /^\[.*\]$/.test(v.trim());

/** Safe external link: returns "#" for placeholders so the build never emits broken URLs. */
export const linkOr = (v: string, fallback = '/contact/') => (isPlaceholder(v) ? fallback : v);

export const bookingHref = linkOr(site.bookingUrl, '/contact/#book');
export const phoneHref = site.phoneE164 ? `tel:${site.phoneE164}` : undefined;
export const emailHref = isPlaceholder(site.email) ? undefined : `mailto:${site.email}`;
