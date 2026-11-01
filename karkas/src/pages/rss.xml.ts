import type { APIRoute } from 'astro';
import { SITE } from '../data/site';
import { ARTICLES } from '../data/articles';
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export const GET: APIRoute = () => {
  const items = [...ARTICLES].sort((a, b) => b.date.localeCompare(a.date)).map((a) => `
  <item><title>${esc(a.title)}</title><link>${SITE.url}/novosti/${a.slug}/</link><guid>${SITE.url}/novosti/${a.slug}/</guid><pubDate>${new Date(a.date).toUTCString()}</pubDate><description>${esc(a.description)}</description><category>${esc(a.tag)}</category></item>`).join('');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>${esc(SITE.brand)} — новости и статьи</title><link>${SITE.url}/novosti/</link><description>${esc(SITE.description)}</description><language>ru</language>${items}
</channel></rss>`, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
};
