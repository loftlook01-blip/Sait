/**
 * YML-фид (Яндекс): для Яндекс Бизнеса, товарной галереи в Поиске, смарт-баннеров и динамических объявлений Директа.
 * Адрес фида — /feed.yml. Добавьте его в Яндекс Вебмастер → «Товары и прайс-листы» и в Яндекс Директ.
 */
import type { APIRoute } from 'astro';
import { SITE } from '../data/site';
import { MODELS } from '../data/models';
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
export const GET: APIRoute = () => {
  const date = new Date().toISOString().slice(0, 16).replace('T', ' ');
  const offers = MODELS.map((m) => `
      <offer id="${m.slug}" available="true">
        <url>${SITE.url}/doma/${m.slug}/</url>
        <price>${m.price}</price>
        <currencyId>RUR</currencyId>
        <categoryId>${m.category === 'house' ? 1 : 2}</categoryId>
        <picture>${SITE.url}/images/${m.img}.webp</picture>
        <name>${esc(`${m.kind} «${m.name}» ${m.area} м²`)}</name>
        <vendor>${esc(SITE.brand)}</vendor>
        <description>${esc(m.lead)}</description>
        <sales_notes>${esc('Под ключ со сваями и монтажом. Ипотека 3–6%, эскроу.')}</sales_notes>
        <param name="Площадь" unit="м²">${m.area}</param>
        <param name="Спальни">${m.bedrooms}</param>
        <param name="Габариты" unit="м">${m.size[0]}×${m.size[1]}</param>
        <param name="Срок производства" unit="дней">${m.productionDays}</param>
      </offer>`).join('');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>
<yml_catalog date="${date}">
  <shop>
    <name>${esc(SITE.brand)}</name>
    <company>${esc(SITE.legalName)}</company>
    <url>${SITE.url}</url>
    <currencies><currency id="RUR" rate="1"/></currencies>
    <categories>
      <category id="1">Модульные дома</category>
      <category id="2">Бани, хозблоки, беседки</category>
    </categories>
    <offers>${offers}
    </offers>
  </shop>
</yml_catalog>`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
