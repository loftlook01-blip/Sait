import type { APIRoute } from 'astro';
import { SITE } from '../data/site';
export const GET: APIRoute = () =>
  new Response(JSON.stringify({
    name: `${SITE.brand} — ${SITE.brandSub}`, short_name: SITE.brand, lang: 'ru', start_url: '/', display: 'standalone',
    background_color: '#eceeec', theme_color: '#24514a',
    icons: [{ src: '/icon-512.png', sizes: '512x512', type: 'image/png' }, { src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' }],
  }), { headers: { 'Content-Type': 'application/manifest+json' } });
