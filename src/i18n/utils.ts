import { defaultLang, languages, ui, type Lang, type UIKey } from './ui';

/** Resolve the language from Astro.currentLocale (falls back to English). */
export function getLang(locale: string | undefined): Lang {
  return locale && locale in languages ? (locale as Lang) : defaultLang;
}

/** t('cta.book') → "Book a Free Call" in the current language. */
export function useTranslations(lang: Lang) {
  return (key: UIKey): string => (ui[lang] as Record<string, string>)[key] ?? ui[defaultLang][key];
}

/** Prefix a path with the language (no prefix for English). */
export function localizePath(path: string, lang: Lang): string {
  return lang === defaultLang ? path : `/${lang}${path}`;
}
