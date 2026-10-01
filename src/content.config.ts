import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { categorySlugs } from './data/blog-categories';

/**
 * Blog posts live in src/content/blog/<lang>/<slug>.md
 * The file name becomes the URL: src/content/blog/en/my-post.md → /blog/my-post/
 */
const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: ({ image }) =>
    z.object({
      title: z.string().max(80),
      /** Meta description: aim for 140–160 characters. */
      description: z.string().min(50).max(170),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      category: z.enum(categorySlugs),
      tags: z.array(z.string()).default([]),
      cover: image(),
      coverAlt: z.string(),
      draft: z.boolean().default(false),
    }),
});

export const collections = { blog };
