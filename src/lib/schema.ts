/** JSON-LD structured data builders. */
import { isPlaceholder, site } from '../config/site';
import type { FAQ } from '../data/en/faqs';

const abs = (path: string) => new URL(path, site.url).href;
export const BUSINESS_ID = `${site.url}/#business`;
export const WEBSITE_ID = `${site.url}/#website`;

const stripHtml = (s: string) => s.replace(/<[^>]+>/g, '');

const sameAs = Object.values(site.social).filter((v) => v && !isPlaceholder(v));

export function businessSchema() {
  return {
    '@type': 'ProfessionalService',
    '@id': BUSINESS_ID,
    name: site.name,
    legalName: isPlaceholder(site.legalName) ? undefined : site.legalName,
    url: abs('/'),
    description: site.description,
    logo: abs('/icon-512.png'),
    image: abs(site.ogImage),
    telephone: site.phoneE164 || undefined,
    email: isPlaceholder(site.email) ? undefined : site.email,
    priceRange: '$$',
    address: {
      '@type': 'PostalAddress',
      addressLocality: site.address.locality,
      addressRegion: site.address.region,
      postalCode: site.address.postalCode,
      addressCountry: site.address.country,
    },
    areaServed: { '@type': 'Country', name: 'United States' },
    knowsLanguage: ['en', 'pt', 'es'],
    founder: isPlaceholder(site.founder) ? undefined : { '@type': 'Person', name: site.founder },
    sameAs: sameAs.length ? sameAs : undefined,
    makesOffer: [
      { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Website design and development', url: abs('/web-design/') } },
      { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Local SEO', url: abs('/local-seo/') } },
      { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Social media management', url: abs('/social-media/') } },
    ],
  };
}

export function websiteSchema() {
  return {
    '@type': 'WebSite',
    '@id': WEBSITE_ID,
    url: abs('/'),
    name: site.name,
    publisher: { '@id': BUSINESS_ID },
    inLanguage: 'en-US',
  };
}

export function breadcrumbSchema(items: { name: string; href: string }[]) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.name,
      item: abs(item.href),
    })),
  };
}

export function faqSchema(faqs: FAQ[]) {
  return {
    '@type': 'FAQPage',
    mainEntity: faqs.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: stripHtml(f.a) },
    })),
  };
}

export interface OfferInput {
  name: string;
  price: number;
  monthly?: boolean;
  description?: string;
}

export function serviceSchema(opts: {
  name: string;
  serviceType: string;
  description: string;
  path: string;
  offers: OfferInput[];
}) {
  return {
    '@type': 'Service',
    '@id': `${abs(opts.path)}#service`,
    name: opts.name,
    serviceType: opts.serviceType,
    description: opts.description,
    url: abs(opts.path),
    provider: { '@id': BUSINESS_ID },
    areaServed: { '@type': 'Country', name: 'United States' },
    availableLanguage: ['en', 'pt', 'es'],
    hasOfferCatalog: {
      '@type': 'OfferCatalog',
      name: `${opts.name} plans`,
      itemListElement: opts.offers.map((o) => ({
        '@type': 'Offer',
        name: o.name,
        description: o.description,
        priceCurrency: 'USD',
        price: o.price,
        ...(o.monthly
          ? {
              priceSpecification: {
                '@type': 'UnitPriceSpecification',
                price: o.price,
                priceCurrency: 'USD',
                unitCode: 'MON',
                referenceQuantity: { '@type': 'QuantitativeValue', value: 1, unitCode: 'MON' },
              },
            }
          : { priceSpecification: { '@type': 'PriceSpecification', minPrice: o.price, priceCurrency: 'USD' } }),
      })),
    },
  };
}

export function blogPostingSchema(post: {
  title: string;
  description: string;
  path: string;
  image: string;
  datePublished: Date;
  dateModified?: Date;
  category: string;
  wordCount?: number;
}) {
  return {
    '@type': 'BlogPosting',
    '@id': `${abs(post.path)}#article`,
    headline: post.title,
    description: post.description,
    url: abs(post.path),
    mainEntityOfPage: abs(post.path),
    image: post.image,
    datePublished: post.datePublished.toISOString(),
    dateModified: (post.dateModified ?? post.datePublished).toISOString(),
    articleSection: post.category,
    wordCount: post.wordCount,
    inLanguage: 'en-US',
    author: isPlaceholder(site.founder)
      ? { '@type': 'Organization', name: site.name, url: abs('/') }
      : { '@type': 'Person', name: site.founder, url: abs('/about/') },
    publisher: { '@id': BUSINESS_ID },
  };
}

/** Wrap one or more nodes in a single @graph document. */
export const graph = (nodes: object[]) => ({ '@context': 'https://schema.org', '@graph': nodes });
