import type { APIRoute } from 'astro';
import { SITE } from '../data/site';

export const GET: APIRoute = () =>
  new Response(
    `User-agent: *
Allow: /
Disallow: /api/
Disallow: /styleguide/

# AI-поисковики и ассистенты: разрешаем — это источник трафика из ответов нейросетей (GEO)
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: YandexAdditional
Allow: /

Clean-param: utm_source&utm_medium&utm_campaign&utm_content&utm_term&yclid&gclid&etext

Sitemap: ${SITE.url}/sitemap-index.xml
`,
    { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
  );
