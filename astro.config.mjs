import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { SITE } from './src/data/site.ts';

// https://astro.build/config
export default defineConfig({
  site: SITE.url,
  trailingSlash: 'always',
  prefetch: { prefetchAll: true, defaultStrategy: 'hover' },
  build: { inlineStylesheets: 'always', format: 'directory' },
  compressHTML: true,
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/404') && !page.includes('/spasibo/') && !page.includes('/styleguide/'),
      changefreq: 'weekly',
      priority: 0.7,
      serialize(item) {
        const path = new URL(item.url).pathname;
        if (path === '/') item.priority = 1.0;
        else if (path.startsWith('/uslugi/') || path === '/ceny/') item.priority = 0.9;
        return item;
      },
    }),
  ],
});
