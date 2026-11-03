/**
 * Главный конфиг бренда. Контакты, реквизиты и обещания меняются только здесь —
 * они подставятся во все страницы, микроразметку schema.org, llms.txt и YML-фид.
 *
 * ⚠️ Перед запуском замените значения с пометкой TODO на реальные.
 */
export const SITE = {
  /** TODO: финальный домен (без слеша в конце) */
  url: 'https://hvoya-dom.ru',
  brand: 'ХВОЯ',
  brandSub: 'модульные дома',
  legalName: 'ООО «Хвоя»', // TODO: точное юрлицо
  inn: '', // TODO: ИНН — появится в подвале и разметке, когда заполнен
  ogrn: '', // TODO
  tagline: 'Модульные каркасные дома под ключ с заводской сборкой',
  description:
    'Модульные каркасные дома под ключ в Архангельске и области: 85% дома собирается в цеху за 30 дней, монтаж на участке от 1 дня. Фиксированная смета, ипотека 3–6%, гарантия 5 лет.',

  phone: '+7 (960) 001-08-96',
  phoneHref: '+79600010896',
  email: 'hello@hvoya-dom.ru', // TODO: рабочая почта
  telegram: 'https://t.me/+79600010896', // TODO: можно заменить на @username
  whatsapp: 'https://wa.me/79600010896',
  max: '', // TODO: ссылка на мессенджер MAX
  vk: 'https://vk.com/hvoya_dom', // TODO

  hours: { label: 'Пн–Сб 9:00–19:00', schema: ['Mo-Sa 09:00-19:00'] },

  /** Производство и шоурум (выставочный дом) */
  factory: {
    address: 'г. Архангельск, Лахтинское шоссе, 1', // TODO
    lat: 64.5732, // TODO: точные координаты цеха
    lng: 40.5361,
    showHouse: 'Выставочный дом «Барн 36» у цеха — открыт по записи',
  },

  /** Обещания, которые фиксируются в договоре */
  promises: {
    guaranteeMonths: 60,
    productionDays: 30,
    assemblyDays: 14,
    totalDays: 45,
    factoryReady: 85, // % готовности модуля на заводе
    ceiling: 3, // м — высота потолка в коньке «от»
  },

  analytics: {
    yandexMetrikaId: '', // TODO: номер счётчика Метрики (цели: lead, calc, call, messenger)
    yandexVerification: '', // TODO: код из Яндекс Вебмастера
    googleVerification: '',
  },

  forms: { endpoint: '/api/lead.php' },

  /** Карточки компании — важно для локального SEO и доверия */
  listings: {
    yandexMaps: '', // TODO
    twoGis: '', // TODO
    avito: '', // TODO
  },

  /** Банки-партнёры (аккредитация) */
  banks: ['ДОМ.РФ', 'Сбербанк', 'Россельхозбанк', 'ВТБ'],
} as const;

export const fmt = {
  rub: (n: number) => new Intl.NumberFormat('ru-RU').format(Math.round(n)) + ' ₽',
  num: (n: number) => new Intl.NumberFormat('ru-RU').format(n),
  mln: (n: number) => (n / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 2 }) + ' млн ₽',
};

/** plural(3, ['день', 'дня', 'дней']) → 'дня' */
export const plural = (n: number, forms: [string, string, string]) => {
  const a = Math.abs(n) % 100;
  const b = a % 10;
  if (a > 10 && a < 20) return forms[2];
  if (b > 1 && b < 5) return forms[1];
  if (b === 1) return forms[0];
  return forms[2];
};

export const days = (n: number) => `${n} ${plural(n, ['день', 'дня', 'дней'])}`;

/** Аннуитетный платёж */
export function monthly(principal: number, ratePct: number, years: number) {
  const r = ratePct / 100 / 12;
  const n = years * 12;
  if (principal <= 0) return 0;
  if (r === 0) return principal / n;
  return (principal * r) / (1 - Math.pow(1 + r, -n));
}
