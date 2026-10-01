/**
 * Single entry point for translatable content.
 * When Portuguese/Spanish are added, create src/data/pt/ (copy of en/) and
 * register it here. Pages call getContent(lang) and never import en/ directly.
 */
import type { Lang } from '../i18n/ui';
import * as enPricing from './en/pricing';
import * as enServices from './en/services';
import { faqs as enFaqs } from './en/faqs';
import { testimonials as enTestimonials } from './en/testimonials';
import { caseStudies as enCaseStudies } from './en/portfolio';

const content = {
  en: {
    pricing: enPricing,
    services: enServices,
    faqs: enFaqs,
    testimonials: enTestimonials,
    caseStudies: enCaseStudies,
  },
};

export const getContent = (lang: Lang) => content[lang] ?? content.en;
