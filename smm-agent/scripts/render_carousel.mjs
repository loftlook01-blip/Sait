#!/usr/bin/env node
/**
 * Вёрстка карусели 1080×1350 в PNG по фирменному шаблону templates/carousel.html.
 *
 *   node scripts/render_carousel.mjs data/carousels/2026-11-20-oak/slides.json data/carousels/2026-11-20-oak
 *
 * slides.json: { "brand": "Северная мастерская", "handle": "vk.com/severmasterskaya", "slides": [ ... ] }
 * Типы слайдов (поле "type"):
 *   cover   — { kicker, title, lead?, image?, theme? }         обложка-крючок (image → фото на фоне)
 *   text    — { kicker?, title?, body, image?, theme? }        мысль/объяснение (**жирный** → акцент)
 *   list    — { kicker?, title, items: [..] , theme? }         нумерованный список (до 5 пунктов)
 *   compare — { title, left:{name, points[]}, right:{...} }    сравнение двух вариантов
 *   number  — { big, title, body? }                            крупная цифра/факт
 *   photo   — { image, title?, body?, note? }                  фото на весь слайд с подписью; note — «Концепт» и т.п.
 *   cta     — { title, body, button }                          призыв в конце
 * theme: "light" (по умолчанию), "dark", "pine". Пути к картинкам — относительно slides.json.
 */
import { readFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = dirname(fileURLToPath(import.meta.url));
const [, , specPath, outDir = dirname(specPath ?? '.')] = process.argv;
if (!specPath) { console.error('usage: render_carousel.mjs slides.json [out_dir]'); process.exit(1); }

const spec = JSON.parse(readFileSync(specPath, 'utf8'));
const base = dirname(resolve(specPath));
const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const rich = (s = '') => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
const img = (p) => {
  if (!p) return '';
  const abs = /^https?:/.test(p) ? p : pathToFileURL(resolve(base, p)).href;
  if (!/^https?:/.test(p) && !existsSync(resolve(base, p))) console.warn('нет картинки:', p);
  return abs;
};

function html(s, i, n) {
  const theme = s.image && ['cover', 'photo'].includes(s.type) ? 'photo' : (s.theme || (s.type === 'cta' ? 'dark' : 'light'));
  const bg = theme === 'photo' ? `<div class="bg" style="background-image:url('${img(s.image)}')"></div>` : '';
  const note = s.note ? `<div class="note">${esc(s.note)}</div>` : '';
  let inner = '';
  switch (s.type) {
    case 'cover':
      inner = `${s.kicker ? `<div class="kicker">${esc(s.kicker)}</div>` : ''}<h1>${rich(s.title)}</h1>${s.lead ? `<p class="lead">${rich(s.lead)}</p>` : ''}<div class="swipe">Листайте →</div>`;
      if (theme !== 'photo') inner = `<div class="grow"></div>${inner}<div class="grow"></div>`;
      break;
    case 'list':
      inner = `${s.kicker ? `<div class="kicker">${esc(s.kicker)}</div>` : ''}<h2>${rich(s.title)}</h2><ul class="list">${(s.items || []).map((x) => `<li><span>${rich(x)}</span></li>`).join('')}</ul>`;
      break;
    case 'compare': {
      const col = (c) => `<div class="col"><h3>${esc(c.name)}</h3>${(c.points || []).map((p) => `<p>${rich(p)}</p>`).join('')}</div>`;
      inner = `${s.kicker ? `<div class="kicker">${esc(s.kicker)}</div>` : ''}<h2>${rich(s.title)}</h2><div class="cmp">${col(s.left)}${col(s.right)}</div>`;
      break;
    }
    case 'number':
      inner = `<div class="grow"></div><div class="big">${esc(s.big)}</div><h2 style="margin-top:36px">${rich(s.title)}</h2>${s.body ? `<p class="body">${rich(s.body)}</p>` : ''}<div class="grow"></div>`;
      break;
    case 'photo':
      inner = `${s.title ? `<h2>${rich(s.title)}</h2>` : ''}${s.body ? `<p class="body">${rich(s.body)}</p>` : ''}`;
      break;
    case 'cta':
      inner = `<div class="grow"></div><h2>${rich(s.title)}</h2><p class="body">${rich(s.body)}</p><div class="grow"></div><div class="cta">${esc(s.button || 'Написать в сообщения')}</div>`;
      break;
    default: // text
      inner = `${s.kicker ? `<div class="kicker">${esc(s.kicker)}</div>` : ''}${s.title ? `<h2>${rich(s.title)}</h2>` : ''}<p class="body">${rich(s.body)}</p>${s.image ? `<div class="img" style="background-image:url('${img(s.image)}')"></div>` : ''}`;
  }
  if (['list', 'compare'].includes(s.type) || (s.type === 'text' && !s.image)) inner = `<div class="grow"></div>${inner}<div class="grow" style="flex:1.4"></div>`;
  const dots = Array.from({ length: n }, (_, k) => `<i class="${k === i ? 'on' : ''}"></i>`).join('');
  return `<section class="slide ${theme}">${bg}${note}${inner}<div class="footer"><span>${esc(spec.brand || 'Северная мастерская')} · ${esc(spec.handle || '')}</span><span class="dots">${dots}</span></div></section>`;
}

mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(join(here, '..', 'templates', 'carousel.html')).href, { waitUntil: 'networkidle', timeout: 20000 }).catch(() => {});
const n = spec.slides.length;
for (let i = 0; i < n; i++) {
  await page.evaluate((h) => { document.getElementById('root').innerHTML = h; }, html(spec.slides[i], i, n));
  await page.evaluate(() => Promise.all([...document.images].map((im) => im.decode().catch(() => {}))).then(() => document.fonts.ready));
  await page.waitForTimeout(150);
  // проверка переполнения: текст не должен вылезать за слайд
  const overflow = await page.evaluate(() => { const s = document.querySelector('.slide'); return s.scrollHeight > s.clientHeight + 2; });
  if (overflow) console.warn(`⚠ слайд ${i + 1}: текст не помещается — сократите`);
  const file = join(outDir, `${String(i + 1).padStart(2, '0')}.png`);
  await page.locator('.slide').screenshot({ path: file });
  console.log(file);
}
await browser.close();
