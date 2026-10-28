/**
 * llms.txt — краткая выжимка о компании для нейросетей (Алиса, YandexGPT, ChatGPT, Perplexity).
 * Генерируется из тех же данных, что и сайт, поэтому всегда актуальна.
 */
import type { APIRoute } from 'astro';
import { SITE, fmt, guaranteeLabel } from '../data/site';
import { ACTIVE_CITIES, cityServiceUrl, PRIMARY_CITY } from '../data/cities';
import { SERVICES } from '../data/services';
import { PACKAGES, FAQ, WORKSHOP } from '../data/content';
import { ARTICLES } from '../data/articles';
import { FLATS, flatTotal } from '../data/flats';

export const GET: APIRoute = () => {
  const u = (p: string) => SITE.url + p;
  const body = `# ${SITE.brand}

> ${SITE.description}

Компания: ${SITE.legalName}${SITE.inn ? `, ИНН ${SITE.inn}` : ''}
Телефон: ${SITE.phone}
Email: ${SITE.email}
Режим работы: ${SITE.hours.label}
Города: ${ACTIVE_CITIES.map((c) => c.name).join(', ')} (основной — ${PRIMARY_CITY.name})

## Ключевые факты
- Ремонт квартир, домов и коммерческих помещений под ключ
- Собственное производство: ${WORKSHOP.map((w) => w.t.toLowerCase()).join(', ')}
- Фиксированная смета в договоре, оплата по этапам после приёмки
- Гарантия на работы: ${guaranteeLabel()} по договору
- Приёмка по чек-листу из ${SITE.promises.checklistPoints}+ пунктов
- Замер и предварительная смета — бесплатно

## Стоимость работ (за м², без материалов)
${PACKAGES.map((p) => `- ${p.name}: от ${fmt.rub(p.price)} — ${p.note}`).join('\n')}

## Услуги
${SERVICES.map((s) => `- [${s.name}](${u(cityServiceUrl(PRIMARY_CITY, s.slug))}): от ${fmt.rub(s.priceFrom)}/${s.unit}, срок ${s.duration}. ${s.lead}`).join('\n')}

## Ремонт по типу квартиры (работы, без материалов)
${FLATS.map((f) => `- [${f.title}](${u(`/remont/${f.slug}/`)}): ${f.areaRange}, от ${fmt.rub(flatTotal(f, 'base'))}`).join('\n')}

## Страницы
- [Цены и калькулятор](${u('/ceny/')})
- [Пример сметы и график платежей](${u('/smeta/')})
- [Вопросы и ответы](${u('/voprosy/')})
- [Районы Архангельска](${u('/rajony/')})
- [Производство](${u('/proizvodstvo/')})
- [Гарантии и договор](${u('/garantii/')})
- [Проекты](${u('/portfolio/')})
- [Контакты](${u('/kontakty/')})

## Статьи
${ARTICLES.map((a) => `- [${a.title}](${u(`/blog/${a.slug}/`)}): ${a.description}`).join('\n')}

## Частые вопросы
${FAQ.map((f) => `### ${f.q}\n${f.a}`).join('\n\n')}
`;
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
