// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

import sitemap from '@astrojs/sitemap';

import { EventEmitter } from 'events'
EventEmitter.defaultMaxListeners = 100

// https://astro.build/config
export default defineConfig({
	site: 'https://example.com',
	markdown: {
		shikiConfig: {
		  theme: 'material-theme-ocean',
		},
	  },
	integrations: [mdx(), sitemap()],
	vite: {
		server: {
		  hmr: { path: '/vite-hmr/' },
		  allowedHosts: ['localhost', '127.0.0.1', '0.0.0.0', 'devserver-preview--welovepetscare.netlify.app', 'devserver-preview--welovepetscare.netlify.app:3000', 'devserver-preview--welovepetscare.netlify.app:8888'],
		}
	  },
	server: {
		port: 3000,
	  },
});
