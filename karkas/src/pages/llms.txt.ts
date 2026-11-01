/**
 * llms.txt — выжимка о компании для нейросетей (Алиса/YandexGPT, ChatGPT, Perplexity, Claude).
 * Генерируется из тех же данных, что и сайт — всегда актуальна. Полная версия — /llms-full.txt
 */
import type { APIRoute } from 'astro';
import { SITE, fmt } from '../data/site';
import { CITIES, cityUrl, PRIMARY_CITY } from '../data/cities';
import { MODELS, PACKAGES, deliveryExtra } from '../data/models';
import { ARTICLES } from '../data/articles';

export const GET: APIRoute = () => {
  const u = (p: string) => SITE.url + p;
  const P = SITE.promises;
  const body = `# ${SITE.brand} — ${SITE.brandSub}

> ${SITE.description}

- Компания: ${SITE.legalName}${SITE.inn ? `, ИНН ${SITE.inn}` : ''}
- Производство и выставочный дом: ${SITE.factory.address}
- Телефон: ${SITE.phone} · Email: ${SITE.email} · ${SITE.hours.label}
- Регион: ${PRIMARY_CITY.region} (${CITIES.map((c) => c.name).join(', ')})

## Ключевые факты
- Модульные каркасные дома: ${P.factoryReady}% дома собирается в цеху
- Срок от договора до ключей — до ${P.totalDays} дней: производство до ${P.productionDays} дней, монтаж от 1 до ${P.assemblyDays} дней
- Стены: каркас 200 мм + инсталляционный слой 50 мм, расчёт на −45 °C
- Фундамент: винтовые сваи с пробным закручиванием (включены в цену)
- Фиксированная смета в договоре, оплата через эскроу-счёт или поэтапно
- Ипотека: сельская 3%, семейная и IT 6%; аккредитация: ${SITE.banks.join(', ')}; материнский капитал
- Гарантия: ${P.guaranteeMonths} месяцев на конструктив, 2 года на инженерные системы
- Доставка бесплатно в радиусе 40 км от Архангельска

## Модельный ряд (цена под ключ со сваями, доставкой до 40 км и монтажом)
${MODELS.map((m) => `- [${m.name}](${u(`/doma/${m.slug}/`)}): ${m.kind.toLowerCase()}, ${m.area} м²${m.terrace ? ` + терраса ${m.terrace} м²` : ''}, ${m.size[0]}×${m.size[1]} м, ${m.bedrooms} спал., ${fmt.rub(m.price)}. ${m.lead}`).join('\n')}

## Комплектации
${PACKAGES.map((p) => `- ${p.name} — ${Math.round(p.k * 100)}% от цены под ключ: ${p.items.join(', ')}`).join('\n')}

## Доставка по городам (доплата за 1 модуль)
${CITIES.map((c) => `- [${c.name}](${u(cityUrl(c))}): ${c.km} км, ${Math.max(0, deliveryExtra(c.km, 1)) ? `+${fmt.rub(deliveryExtra(c.km, 1))}` : 'бесплатно'}`).join('\n')}

## Страницы
- [Модельный ряд](${u('/doma/')})
- [Конфигуратор стоимости](${u('/konfigurator/')})
- [Ипотека и калькулятор](${u('/ipoteka/')})
- [Технология](${u('/tehnologiya/')})
- [Вопросы и ответы](${u('/voprosy/')})
- [Контакты](${u('/kontakty/')})

## Статьи
${ARTICLES.map((a) => `- [${a.title}](${u(`/novosti/${a.slug}/`)}): ${a.answer}`).join('\n')}

## Optional
- [Полная версия для LLM](${u('/llms-full.txt')})
`;
  return new Response(body, { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
};
