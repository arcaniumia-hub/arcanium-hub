/**
 * Interface text (navigation, buttons, labels).
 * To add a language later: copy the `en` block, change the key to `pt` or `es`
 * and translate the values. Missing keys fall back to English.
 */
export const languages = { en: 'English' } as const;
export const defaultLang = 'en' as const;
export type Lang = keyof typeof languages;

export const ui = {
  en: {
    'cta.book': 'Book a Free Call',
    'cta.quote': 'Get a Free Quote',
    'cta.pricing': 'See Plans & Pricing',
    'nav.services': 'Services',
    'nav.webDesign': 'Web Design',
    'nav.localSeo': 'Local SEO',
    'nav.socialMedia': 'Social Media',
    'nav.pricing': 'Pricing',
    'nav.work': 'Work',
    'nav.about': 'About',
    'nav.blog': 'Blog',
    'nav.contact': 'Contact',
    'nav.home': 'Home',
    'nav.menu': 'Menu',
    'nav.close': 'Close menu',
    'nav.skip': 'Skip to content',
    'footer.blurb':
      'A small-business marketing studio. Websites, local SEO and social media at fair, published prices — with a real person on the other end.',
    'footer.multilingual': 'Se habla español · Falamos português',
    'footer.company': 'Company',
    'footer.contact': 'Contact',
    'footer.privacy': 'Privacy Policy',
    'footer.terms': 'Terms of Service',
    'footer.rights': 'All rights reserved.',
    'footer.based': 'Based in',
    'pricing.from': 'from',
    'pricing.startingAt': 'Starting at',
    'pricing.mo': '/mo',
    'pricing.oneTime': 'one-time',
    'pricing.popular': 'Most Popular',
    'pricing.save': 'Save',
    'pricing.vsSeparately': 'vs. buying separately',
    'pricing.includes': 'Includes',
    'faq.title': 'Frequently asked questions',
    'placeholder.label': 'Placeholder',
    'breadcrumb.label': 'Breadcrumb',
  },
} as const;

export type UIKey = keyof (typeof ui)[typeof defaultLang];
