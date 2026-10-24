/**
 * Главный конфиг бренда. Все контакты, реквизиты и обещания меняются здесь —
 * они автоматически подставятся во все страницы, микроразметку и llms.txt.
 *
 * ⚠️ Перед запуском замените значения, помеченные TODO, на реальные.
 */
export const SITE = {
  /** TODO: финальный домен (без слеша в конце) */
  url: 'https://severmasterskaya.ru',
  brand: 'Северная мастерская',
  brandShort: 'СМ',
  legalName: 'ООО «Северная мастерская»', // TODO
  inn: '', // TODO: ИНН — показывается в подвале и в разметке, когда заполнен
  ogrn: '', // TODO
  tagline: 'Ремонт под ключ с собственным производством',
  description:
    'Ремонт квартир и домов под ключ в Архангельске: дизайн-проект, фиксированная смета в договоре, собственный столярный и сварочный цех с порошковой покраской. Гарантия по договору.',

  phone: '+7 (8182) 00-00-00', // TODO
  phoneHref: '+78182000000', // TODO
  email: 'hello@severmasterskaya.ru', // TODO
  telegram: 'https://t.me/severmasterskaya', // TODO
  whatsapp: 'https://wa.me/78182000000', // TODO
  vk: 'https://vk.com/severmasterskaya', // TODO
  max: '', // TODO: ссылка на мессенджер MAX, если используете

  /** Режим работы (schema.org openingHours) */
  hours: { label: 'Пн–Сб 9:00–20:00', schema: ['Mo-Sa 09:00-20:00'] },

  /** Обещания, которые фиксируются в договоре. Не указывайте то, что не готовы гарантировать. */
  promises: {
    guaranteeYears: 3,
    checklistPoints: 120,
    freeMeasure: true,
    designFrom: 1500, // ₽ за м²
  },

  /** Производство */
  workshop: {
    address: 'г. Архангельск, ул. Производственная, 1', // TODO
    areaM2: 0, // TODO: площадь цеха, м² — блок с цифрой появится, когда заполните
  },

  /** Аналитика. Пустые значения — счётчики не подключаются. */
  analytics: {
    yandexMetrikaId: '', // TODO: номер счётчика Метрики
    yandexVerification: '', // TODO: код из Яндекс Вебмастера
    googleVerification: '',
  },

  /** Куда отправляются заявки. По умолчанию — PHP-обработчик из public/api/lead.php */
  forms: { endpoint: '/api/lead.php' },

  /** Ссылки на карточки компании — важно для локального SEO */
  listings: {
    yandexMaps: '', // TODO: ссылка на организацию в Яндекс Картах
    twoGis: '', // TODO
  },
} as const;

export type Site = typeof SITE;

export const fmt = {
  rub: (n: number) => new Intl.NumberFormat('ru-RU').format(Math.round(n)) + ' ₽',
  num: (n: number) => new Intl.NumberFormat('ru-RU').format(n),
};

/** Склонение: plural(3, ['год', 'года', 'лет']) → 'года' */
export const plural = (n: number, forms: [string, string, string]) => {
  const a = Math.abs(n) % 100;
  const b = a % 10;
  if (a > 10 && a < 20) return forms[2];
  if (b > 1 && b < 5) return forms[1];
  if (b === 1) return forms[0];
  return forms[2];
};

export const guaranteeLabel = () => `${SITE.promises.guaranteeYears} ${plural(SITE.promises.guaranteeYears, ['год', 'года', 'лет'])}`;
