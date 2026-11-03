/**
 * SEO-модуль: генераторы микроразметки schema.org (JSON-LD) для Яндекса, Google и AI-поисковиков.
 * Все данные берутся из src/data — разметка всегда совпадает с тем, что видно на странице.
 */
import { SITE } from '../data/site';
import { CITIES, PRIMARY_CITY, cityUrl, type City } from '../data/cities';
import { FAQ } from '../data/content';
import { gallery, type Model } from '../data/models';
import type { Article } from '../data/articles';

export const abs = (path: string) => new URL(path, SITE.url).href;
export const ORG_ID = `${SITE.url}/#organization`;
export const SITE_ID = `${SITE.url}/#website`;

export function organization() {
  const sameAs = [SITE.vk, SITE.telegram, SITE.listings.yandexMaps, SITE.listings.twoGis, SITE.listings.avito].filter(Boolean);
  return {
    '@context': 'https://schema.org',
    '@type': ['HomeAndConstructionBusiness', 'GeneralContractor'],
    '@id': ORG_ID,
    name: SITE.brand,
    alternateName: `${SITE.brand} — ${SITE.brandSub}`,
    legalName: SITE.legalName,
    ...(SITE.inn ? { taxID: SITE.inn } : {}),
    description: SITE.description,
    slogan: SITE.tagline,
    url: SITE.url,
    logo: abs('/favicon.svg'),
    image: abs('/og.jpg'),
    telephone: SITE.phoneHref,
    email: SITE.email,
    priceRange: '₽₽',
    currenciesAccepted: 'RUB',
    paymentAccepted: 'Безналичный расчёт, ипотека, эскроу-счёт, материнский капитал',
    openingHours: SITE.hours.schema,
    address: {
      '@type': 'PostalAddress',
      streetAddress: SITE.factory.address.replace(/^г\. [^,]+, /, ''),
      addressLocality: PRIMARY_CITY.name,
      addressRegion: PRIMARY_CITY.region,
      addressCountry: 'RU',
    },
    geo: { '@type': 'GeoCoordinates', latitude: SITE.factory.lat, longitude: SITE.factory.lng },
    hasMap: `https://yandex.ru/maps/?pt=${SITE.factory.lng},${SITE.factory.lat}&z=15&l=map`,
    areaServed: [
      { '@type': 'AdministrativeArea', name: PRIMARY_CITY.region },
      ...CITIES.map((c) => ({ '@type': 'City', name: c.name })),
    ],
    knowsAbout: ['модульные дома', 'каркасные дома', 'барнхаус', 'модульные бани', 'винтовые сваи', 'ипотека на ИЖС', 'эскроу-счёт ИЖС'],
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: SITE.phoneHref,
      contactType: 'sales',
      areaServed: 'RU',
      availableLanguage: 'Russian',
    },
    sameAs,
  };
}

export function website() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': SITE_ID,
    url: SITE.url,
    name: SITE.brand,
    description: SITE.description,
    inLanguage: 'ru-RU',
    publisher: { '@id': ORG_ID },
  };
}

export function breadcrumbs(items: { name: string; url: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((it, i) => ({ '@type': 'ListItem', position: i + 1, name: it.name, item: abs(it.url) })),
  };
}

export function faq(items: { q: string; a: string }[] = FAQ) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((i) => ({ '@type': 'Question', name: i.q, acceptedAnswer: { '@type': 'Answer', text: i.a } })),
  };
}

/** Карточка дома: Product + Offer (цена, наличие, продавец) + характеристики */
export function product(m: Model) {
  const url = abs(`/doma/${m.slug}/`);
  return {
    '@context': 'https://schema.org',
    '@type': 'Product',
    '@id': `${url}#product`,
    name: `Модульный дом «${m.name}» — ${m.area} м²`,
    description: m.lead,
    image: gallery(m).map((g) => abs(`/images/${g.img}.webp`)),
    url,
    sku: m.slug,
    brand: { '@type': 'Brand', name: SITE.brand },
    manufacturer: { '@id': ORG_ID },
    category: m.category === 'house' ? 'Модульные дома' : 'Хозпостройки, бани, беседки',
    additionalProperty: [
      { '@type': 'PropertyValue', name: 'Площадь', value: m.area, unitCode: 'MTK' },
      { '@type': 'PropertyValue', name: 'Спальни', value: m.bedrooms },
      { '@type': 'PropertyValue', name: 'Модулей', value: m.modules },
      { '@type': 'PropertyValue', name: 'Высота потолка в коньке', value: m.ceiling, unitCode: 'MTR' },
      { '@type': 'PropertyValue', name: 'Срок производства', value: `${m.productionDays} дней` },
      { '@type': 'PropertyValue', name: 'Фасад', value: m.facade },
    ],
    offers: {
      '@type': 'Offer',
      url,
      priceCurrency: 'RUB',
      price: m.price,
      availability: 'https://schema.org/PreOrder',
      itemCondition: 'https://schema.org/NewCondition',
      seller: { '@id': ORG_ID },
      areaServed: { '@type': 'AdministrativeArea', name: PRIMARY_CITY.region },
      priceValidUntil: `${new Date().getFullYear()}-12-31`,
    },
  };
}

export function itemList(models: Model[], name: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name,
    itemListElement: models.map((m, i) => ({ '@type': 'ListItem', position: i + 1, url: abs(`/doma/${m.slug}/`), name: m.name })),
  };
}

/** Гео-посадочная: услуга в конкретном городе */
export function cityService(c: City, minPrice: number) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Service',
    '@id': `${abs(cityUrl(c))}#service`,
    name: `Модульные дома под ключ ${c.in}`,
    serviceType: 'Производство, доставка и монтаж модульных домов',
    provider: { '@id': ORG_ID },
    areaServed: {
      '@type': 'City',
      name: c.name,
      geo: { '@type': 'GeoCoordinates', latitude: c.lat, longitude: c.lng },
      containedInPlace: { '@type': 'AdministrativeArea', name: c.region },
    },
    offers: { '@type': 'AggregateOffer', priceCurrency: 'RUB', lowPrice: minPrice, offerCount: 6 },
    url: abs(cityUrl(c)),
  };
}

export function article(a: Article) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: a.title,
    description: a.description,
    abstract: a.answer,
    datePublished: a.date,
    dateModified: a.updated ?? a.date,
    mainEntityOfPage: abs(`/novosti/${a.slug}/`),
    image: abs(`/images/${a.img}.webp`),
    author: { '@type': 'Organization', '@id': ORG_ID, name: SITE.brand },
    publisher: { '@id': ORG_ID },
    inLanguage: 'ru-RU',
    articleSection: a.tag,
  };
}

export function howTo(name: string, steps: { t: string; x: string }[], totalDays: number) {
  return {
    '@context': 'https://schema.org',
    '@type': 'HowTo',
    name,
    totalTime: `P${totalDays}D`,
    step: steps.map((s, i) => ({ '@type': 'HowToStep', position: i + 1, name: s.t, text: s.x })),
  };
}
