import { getCollection, type CollectionEntry } from 'astro:content';
import type { Lang } from '../i18n/ui';

export type Post = CollectionEntry<'blog'>;

/** "en/my-post" → "my-post" */
export const postSlug = (post: Post) => post.id.replace(/^[a-z]{2}\//, '');
export const postLang = (post: Post) => post.id.split('/')[0];
export const postUrl = (post: Post) => `/blog/${postSlug(post)}/`;

export async function getPosts(lang: Lang = 'en') {
  const posts = await getCollection('blog', (p) => postLang(p) === lang && (import.meta.env.DEV || !p.data.draft));
  return posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}

export const readingTime = (body = '') => Math.max(1, Math.round(body.split(/\s+/).filter(Boolean).length / 230));
export const wordCount = (body = '') => body.split(/\s+/).filter(Boolean).length;

export const formatDate = (d: Date) =>
  d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
