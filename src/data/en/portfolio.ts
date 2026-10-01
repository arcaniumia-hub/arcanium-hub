/**
 * Portfolio / case studies (English).
 * ⚠️ All three projects are PLACEHOLDERS. Replace the text and images with real
 * projects, then set `placeholder: false`. Never publish invented results.
 *
 * Images live in src/assets/portfolio/. Replace the files (keep the names) or
 * import new ones below. Use landscape images, ideally 1600×1000 or larger.
 *
 * Slugs that start with "placeholder-" are noindexed and kept out of the sitemap.
 * Give real projects a descriptive slug, e.g. "roofing-company-website-charleston".
 */
import type { ImageMetadata } from 'astro';
import imgConstruction from '../../assets/portfolio/placeholder-construction.jpg';
import imgRestaurant from '../../assets/portfolio/placeholder-restaurant.jpg';
import imgClinic from '../../assets/portfolio/placeholder-clinic.jpg';

export interface CaseStudy {
  slug: string;
  title: string;
  clientType: string;
  location: string;
  services: string[];
  image: ImageMetadata;
  imageAlt: string;
  challenge: string;
  whatWeDid: string[];
  results: string[];
  url?: string;
  placeholder: boolean;
  featured?: boolean;
}

export const caseStudies: CaseStudy[] = [
  {
    slug: 'placeholder-construction-company',
    title: 'Construction company — website + Google profile',
    clientType: 'Construction company',
    location: '[City, State]',
    services: ['Website Design', 'Local SEO'],
    image: imgConstruction,
    imageAlt: 'Placeholder image for a construction company website project',
    challenge:
      '[PLACEHOLDER] Describe the problem in one or two sentences. Example: an outdated website that did not work on phones and a Google profile with few photos and no posts.',
    whatWeDid: [
      '[PLACEHOLDER] Designed and built a 7-page website with a page for each service',
      '[PLACEHOLDER] Optimized the Google Business Profile and added project photos',
      '[PLACEHOLDER] Added a quote request form connected to email',
    ],
    results: ['[RESULT — replace with a real, verifiable result, e.g. calls or form leads per month]'],
    placeholder: true,
    featured: true,
  },
  {
    slug: 'placeholder-restaurant',
    title: 'Restaurant — social media management',
    clientType: 'Restaurant',
    location: '[City, State]',
    services: ['Social Media'],
    image: imgRestaurant,
    imageAlt: 'Placeholder image for a restaurant social media project',
    challenge:
      '[PLACEHOLDER] Describe the problem. Example: posting irregularly with no consistent look, and no time to reply to messages.',
    whatWeDid: [
      '[PLACEHOLDER] Created branded templates and a monthly content calendar',
      '[PLACEHOLDER] Produced weekly Reels featuring the menu and team',
      '[PLACEHOLDER] Managed comments and messages',
    ],
    results: ['[RESULT — replace with a real, verifiable result]'],
    placeholder: true,
    featured: true,
  },
  {
    slug: 'placeholder-clinic',
    title: 'Clinic — new website + local SEO',
    clientType: 'Health clinic',
    location: '[City, State]',
    services: ['Website Design', 'Local SEO'],
    image: imgClinic,
    imageAlt: 'Placeholder image for a clinic website and local SEO project',
    challenge:
      '[PLACEHOLDER] Describe the problem. Example: not appearing on Google Maps for the services the clinic wanted to grow.',
    whatWeDid: [
      '[PLACEHOLDER] Built individual pages for each treatment',
      '[PLACEHOLDER] Set up schema markup and local directory listings',
      '[PLACEHOLDER] Started monthly Google profile posts and review requests',
    ],
    results: ['[RESULT — replace with a real, verifiable result]'],
    placeholder: true,
    featured: true,
  },
];
