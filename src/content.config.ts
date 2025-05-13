import { glob, file } from 'astro/loaders';
import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
	// Load Markdown and MDX files in the `src/content/blog/` directory.
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}' }),
	// Type-check frontmatter using a schema
	schema: z.object({
		title: z.string(),
		description: z.string().optional(),
		// Transform string to Date object
		pubDate: z.coerce.date(),
		updatedDate: z.coerce.date().optional(),
		heroImage: z.string().optional(),
	}),
});

const branch = defineCollection({
	loader: glob({ base: './src/content/branch', pattern: '**/*.{md,mdx}' }),
	schema: z.object({
		branchName: z.string(),
		pubDate: z.coerce.date(),
		updatedDate: z.coerce.date().optional(),
	}),
});

const home = defineCollection({
	loader: glob({ base: './src/content/home', pattern: '*.md' }),
	schema: z.object({
		title: z.string(),
		subtitle: z.string(),
		heroVideo: z.string(),
		services: z.array(
			z.object({
				title: z.string(),
				image: z.string(),
				description: z.string(),
			})
		),
		mediaSection: z.object({
			image: z.string(),
			subtitle: z.string(),
			title: z.string(),
			description: z.string(),
		}),
		featuredLogos: z.array(
			z.object({
				title: z.string(),
				image: z.string(),
			})
		),
	}),
});

export const collections = { blog, branch, home };
