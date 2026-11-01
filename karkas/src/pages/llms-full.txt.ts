/** llms-full.txt — весь смысловой контент сайта одним markdown-файлом для AI-ассистентов */
import type { APIRoute } from 'astro';
import { SITE, fmt } from '../data/site';
import { CITIES } from '../data/cities';
import { MODELS } from '../data/models';
import { FAQ, STEPS, WALL_LAYERS, MORTGAGE } from '../data/content';
import { ARTICLES } from '../data/articles';

const strip = (h: string) => h
  .replace(/<h2[^>]*>(.*?)<\/h2>/g, '\n### $1\n')
  .replace(/<li>(.*?)<\/li>/g, '- $1\n')
  .replace(/<tr>(.*?)<\/tr>/g, (_, r) => '| ' + r.replace(/<t[hd]>(.*?)<\/t[hd]>/g, '$1 | ') + '\n')
  .replace(/<a href="([^"]+)">(.*?)<\/a>/g, `[$2](${SITE.url}$1)`)
  .replace(/<\/?(strong|b)>/g, '**')
  .replace(/<[^>]+>/g, '')
  .replace(/\n{3,}/g, '\n\n')
  .trim();

export const GET: APIRoute = () => {
  const body = `# ${SITE.brand} — полная информация

${SITE.description}

Контакты: ${SITE.phone}, ${SITE.email}, ${SITE.factory.address}, ${SITE.hours.label}.

## Дома
${MODELS.map((m) => `### ${m.name} — ${m.area} м², ${fmt.rub(m.price)} под ключ
${m.text.join('\n\n')}
- Габариты: ${m.size[0]}×${m.size[1]} м, модулей: ${m.modules}, потолок в коньке ${m.ceiling} м
- Фасад: ${m.facade}
- Производство: ${m.productionDays} дн., монтаж: ${m.assemblyDays} дн.
- Комнаты: ${m.plan.map((r) => `${r.n} ${(r.w * r.h).toFixed(1)} м²`).join(', ')}
- Особенности: ${m.features.join('; ')}
`).join('\n')}

## Этапы
${STEPS.map((s, i) => `${i + 1}. ${s.t} (${s.d}) — ${s.x}`).join('\n')}

## Пирог стены
${WALL_LAYERS.map((l) => `- ${l.t}${l.mm > 1 ? ` ${l.mm} мм` : ''}: ${l.x}`).join('\n')}

## Ипотека
${MORTGAGE.map((m) => `- ${m.name}: ${m.rate}%, до ${fmt.rub(m.max)}, взнос от ${m.down}%. ${m.note}`).join('\n')}

## География
${CITIES.map((c) => `### ${c.name}\n${c.intro}\n${c.soil}\n${c.roads}`).join('\n\n')}

## Вопросы и ответы
${FAQ.map((f) => `**${f.q}**\n${f.a}`).join('\n\n')}

## Статьи
${ARTICLES.map((a) => `## ${a.title}\n${a.answer}\n\n${strip(a.body)}`).join('\n\n')}
`;
  return new Response(body, { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
};
