import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { site } from '../config/site';
import { getPosts, postUrl } from '../lib/blog';

export async function GET(context: APIContext) {
  const posts = await getPosts('en');
  return rss({
    title: `${site.name} Blog`,
    description: 'Practical guides on websites, local SEO and social media for small businesses.',
    site: context.site!,
    items: posts.map((p) => ({
      title: p.data.title,
      description: p.data.description,
      pubDate: p.data.pubDate,
      link: postUrl(p),
    })),
  });
}
