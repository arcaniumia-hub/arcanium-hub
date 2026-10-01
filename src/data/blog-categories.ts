/** Blog categories. The key is the URL slug: /blog/category/<slug>/ */
export const categories = {
  'web-design': { name: 'Web Design', description: 'Practical advice on planning, pricing and building a small-business website that brings in customers.', service: '/web-design/' },
  'local-seo': { name: 'Local SEO', description: 'How to show up on Google Search and Google Maps when nearby customers look for what you do.', service: '/local-seo/' },
  'social-media': { name: 'Social Media', description: 'Simple, realistic social media strategies for busy small-business owners.', service: '/social-media/' },
} as const;

export type CategorySlug = keyof typeof categories;
export const categorySlugs = Object.keys(categories) as [CategorySlug, ...CategorySlug[]];
