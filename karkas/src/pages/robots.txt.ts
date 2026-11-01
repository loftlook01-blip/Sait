import type { APIRoute } from 'astro';
import { SITE } from '../data/site';

export const GET: APIRoute = () =>
  new Response(
    `User-agent: *
Allow: /
Disallow: /api/
Disallow: /spasibo/
Disallow: /*?*m=

# GEO: AI-поисковики и ассистенты — разрешаем, это трафик из ответов нейросетей
User-agent: YandexAdditional
Allow: /
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /

# Яндекс: не индексировать параметры рекламы и конфигуратора
Clean-param: utm_source&utm_medium&utm_campaign&utm_content&utm_term&yclid&gclid&etext /
Clean-param: m&p&f&fd&t&c&km&o /konfigurator/

Sitemap: ${SITE.url}/sitemap-index.xml
Host: ${SITE.url.replace(/^https?:\/\//, '')}
`,
    { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
  );
