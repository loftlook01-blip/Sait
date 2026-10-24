import type { APIRoute } from 'astro';
import { SITE } from '../data/site';

export const GET: APIRoute = () =>
  new Response(
    JSON.stringify({
      name: SITE.brand,
      short_name: SITE.brand,
      description: SITE.tagline,
      lang: 'ru',
      start_url: '/',
      display: 'standalone',
      background_color: '#f4f1ec',
      theme_color: '#1f1d19',
      icons: [
        { src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' },
        { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
        { src: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
      ],
    }),
    { headers: { 'Content-Type': 'application/manifest+json' } },
  );
