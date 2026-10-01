// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';
import tailwindcss from '@tailwindcss/vite';
import { SITE_URL } from './src/config/site-url.mjs';

export default defineConfig({
  site: SITE_URL,
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'always' },
  // English is the default locale and has no URL prefix.
  // To add Portuguese/Spanish later: add 'pt' and/or 'es' to `locales`
  // (see README → "Adding Portuguese and Spanish").
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
    routing: { prefixDefaultLocale: false },
  },
  integrations: [
    mdx(),
    sitemap({
      filter: (page) => !/\/(thank-you|404)\/?$/.test(page) && !page.includes('/placeholder-'),
    }),
  ],
  image: { responsiveStyles: true },
  // Cast: @tailwindcss/vite ships types for a newer Vite than Astro 5 bundles (harmless).
  vite: { plugins: [/** @type {any} */ (tailwindcss())] },
});
