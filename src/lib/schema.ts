/** Генераторы микроразметки schema.org (JSON-LD) — для Яндекса, Google и AI-поисковиков */
import { SITE } from '../data/site';
import { ACTIVE_CITIES, PRIMARY_CITY, type City } from '../data/cities';
import type { Service } from '../data/services';

const abs = (path: string) => new URL(path, SITE.url).href;
export const ORG_ID = `${SITE.url}/#organization`;

export function organization(city: City = PRIMARY_CITY) {
  const sameAs = [SITE.vk, SITE.telegram, SITE.listings.yandexMaps, SITE.listings.twoGis].filter(Boolean);
  return {
    '@context': 'https://schema.org',
    '@type': ['GeneralContractor', 'HomeAndConstructionBusiness'],
    '@id': ORG_ID,
    name: SITE.brand,
    legalName: SITE.legalName,
    ...(SITE.inn ? { taxID: SITE.inn } : {}),
    description: SITE.description,
    url: SITE.url,
    logo: abs('/favicon.svg'),
    image: abs('/og.jpg'),
    telephone: SITE.phoneHref,
    email: SITE.email,
    priceRange: '₽₽–₽₽₽',
    currenciesAccepted: 'RUB',
    paymentAccepted: 'Наличные, банковская карта, безналичный расчёт',
    openingHours: SITE.hours.schema,
    address: {
      '@type': 'PostalAddress',
      addressLocality: city.name,
      addressRegion: city.region,
      addressCountry: 'RU',
      ...(city.address ? { streetAddress: city.address } : {}),
    },
    geo: { '@type': 'GeoCoordinates', latitude: city.lat, longitude: city.lng },
    areaServed: ACTIVE_CITIES.map((c) => ({ '@type': 'City', name: c.name })),
    knowsAbout: [
      'ремонт квартир под ключ',
      'дизайн интерьера',
      'столярное производство',
      'сварочные работы',
      'порошковая покраска',
    ],
    sameAs,
  };
}

export function service(s: Service, city: City, url: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: `${s.name} ${city.in}`,
    serviceType: s.name,
    description: s.lead,
    url: abs(url),
    provider: { '@id': ORG_ID },
    areaServed: { '@type': 'City', name: city.name },
    offers: {
      '@type': 'Offer',
      priceCurrency: 'RUB',
      priceSpecification: {
        '@type': 'UnitPriceSpecification',
        price: s.priceFrom,
        priceCurrency: 'RUB',
        unitText: s.unit,
        minPrice: s.priceFrom,
      },
    },
  };
}

export function faq(items: { q: string; a: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((i) => ({
      '@type': 'Question',
      name: i.q,
      acceptedAnswer: { '@type': 'Answer', text: i.a },
    })),
  };
}

export function breadcrumbs(items: { name: string; url: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((it, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: it.name,
      item: abs(it.url),
    })),
  };
}

export function article(a: { title: string; description: string; url: string; date: string }) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: a.title,
    description: a.description,
    datePublished: a.date,
    dateModified: a.date,
    mainEntityOfPage: abs(a.url),
    author: { '@id': ORG_ID },
    publisher: { '@id': ORG_ID },
    image: abs('/og.jpg'),
    inLanguage: 'ru-RU',
  };
}

export function website() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${SITE.url}/#website`,
    url: SITE.url,
    name: SITE.brand,
    inLanguage: 'ru-RU',
    publisher: { '@id': ORG_ID },
  };
}
