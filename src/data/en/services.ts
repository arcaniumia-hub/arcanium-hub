/** The three core services (English). Used on the home page, footer and service pages. */

export interface Service {
  id: 'web-design' | 'local-seo' | 'social-media';
  href: string;
  name: string;
  /** Used for the Service schema's serviceType. */
  serviceType: string;
  headline: string;
  summary: string;
  points: string[];
  icon: 'browser' | 'pin' | 'chat';
}

export const services: Service[] = [
  {
    id: 'web-design',
    href: '/web-design/',
    name: 'Website Design',
    serviceType: 'Web design and development',
    headline: 'A website that turns visitors into calls',
    summary:
      'Fast, mobile-first websites built to rank on Google and make it easy for customers to contact you.',
    points: ['Custom design, no cookie-cutter templates', 'Built for speed and SEO', 'Clear quote and contact forms'],
    icon: 'browser',
  },
  {
    id: 'local-seo',
    href: '/local-seo/',
    name: 'Local SEO',
    serviceType: 'Local search engine optimization',
    headline: 'Show up when customers search nearby',
    summary:
      'We optimize your Google Business Profile and website so you appear in the map pack and local results.',
    points: ['Google Business Profile optimization', 'On-page and technical SEO', 'Monthly report in plain English'],
    icon: 'pin',
  },
  {
    id: 'social-media',
    href: '/social-media/',
    name: 'Social Media',
    serviceType: 'Social media management',
    headline: 'Stay active without the daily grind',
    summary:
      'Consistent posts, Reels and replies on Instagram, Facebook, LinkedIn or TikTok — planned, created and published for you.',
    points: ['Content calendar you approve', 'Branded graphics and Reels', 'Community management'],
    icon: 'chat',
  },
];

export const howItWorks = [
  {
    title: 'Free call',
    text: 'A 20-minute conversation about your business, your customers and your goals. No pressure, no jargon.',
  },
  {
    title: 'Clear proposal',
    text: 'Within a few days you get a written plan with exact prices, timelines and what is included. No surprises.',
  },
  {
    title: 'Launch & grow',
    text: 'We build, launch and keep improving. You get simple monthly reports and a direct line to the founder.',
  },
];

export const webDesignProcess = [
  { title: 'Discovery', text: 'We learn about your services, customers and competitors, and agree on the pages you need.' },
  { title: 'Structure & content', text: 'We plan each page around what customers search for and what makes them call.' },
  { title: 'Design', text: 'You see the design before we build. Your feedback shapes every revision round.' },
  { title: 'Build & SEO', text: 'We build a fast, accessible site with on-page SEO, schema and analytics in place.' },
  { title: 'Launch & support', text: 'We launch, test every form, submit your sitemap to Google and stay on call after launch.' },
];

export const seoProcess = [
  { title: 'Audit', text: 'We check your website, Google Business Profile and competitors to find what is holding you back.' },
  { title: 'Fix the foundation', text: 'Profile optimization, on-page SEO, schema and directory listings — the one-time setup.' },
  { title: 'Grow every month', text: 'Fresh Google posts, new citations, content and reviews keep your rankings climbing.' },
  { title: 'Report', text: 'A short monthly report: where you rank, how many calls and clicks you got, and what is next.' },
];

export const socialProcess = [
  { title: 'Setup', text: 'We optimize your profiles and build branded templates that look like your business.' },
  { title: 'Plan', text: 'Every month you get a content calendar to approve. Change anything you like.' },
  { title: 'Create & publish', text: 'We design, write and schedule posts, Reels and stories on the right days and times.' },
  { title: 'Engage & report', text: 'We reply to comments and messages (on Plus and Pro) and report what is working.' },
];
