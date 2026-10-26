// Тестовая сборка для просмотра на любом статическом хостинге (в т.ч. превью по ссылке):
//  - формы в демо-режиме (PUBLIC_DEMO=true) — заявки никуда не отправляются;
//  - все абсолютные пути переписаны в относительные, ссылки на папки → index.html.
// Запуск: node scripts/make-preview.mjs → папка .preview/
import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync, readdirSync, statSync, rmSync, renameSync } from 'node:fs';
import { join, relative, sep, dirname, basename } from 'node:path';
import { buildSync } from 'esbuild';

const OUT = '.preview';
rmSync(OUT, { recursive: true, force: true });
execSync(`npx astro build --outDir ${OUT}`, { stdio: 'inherit', env: { ...process.env, PUBLIC_DEMO: 'true' } });
rmSync(join(OUT, 'api'), { recursive: true, force: true });
rmSync(join(OUT, '.htaccess'), { force: true });
for (const f of ['site.webmanifest', 'sitemap-0.xml', 'sitemap-index.xml', 'robots.txt', 'images/.gitkeep']) rmSync(join(OUT, f), { force: true });
// Некоторые хостинги превью резервируют имена, начинающиеся с «_»
renameSync(join(OUT, '_astro'), join(OUT, 'assets'));

const walk = (d) => readdirSync(d).flatMap((f) => (statSync(join(d, f)).isDirectory() ? walk(join(d, f)) : [join(d, f)]));
const files = walk(OUT);
const pending = [];


const fix = (url, prefix) => {
  if (!url.startsWith('/') || url.startsWith('//')) return url;
  const m = url.match(/^([^?#]*)(.*)$/);
  let [, path, rest] = m;
  if (path.endsWith('/')) path += 'index.html';
  return prefix + path.slice(1) + rest;
};

for (const f of files) {
  const rel = relative(OUT, f).split(sep).join('/');
  if (f.endsWith('.html')) {
    const depth = rel.split('/').length - 1;
    const prefix = depth ? '../'.repeat(depth) : './';
    let h = readFileSync(f, 'utf8');
    h = h.replace(/\b(href|src|action)="([^"]*)"/g, (_, a, u) => `${a}="${fix(u, prefix)}"`);
    h = h.replace(/\bsrcset="([^"]*)"/g, (_, s) => `srcset="${s.split(',').map((p) => { const [u, w] = p.trim().split(/\s+/); return `${fix(u, prefix)} ${w ?? ''}`.trim(); }).join(', ')}"`);
    h = h.replace(/url\(\/_astro\//g, `url(${prefix}_astro/`);
    h = h.replace(/_astro\//g, 'assets/').replace(/<link rel="manifest"[^>]*>/, '');
    pending.push([f, prefix]);
    writeFileSync(f, h);
  } else if (f.endsWith('.css') || f.endsWith('.js')) {
    writeFileSync(f, readFileSync(f, 'utf8').replace(/url\(\/_astro\//g, 'url(./').replace(/\/_astro\//g, './'));
  }
}
// Встраиваем CSS, JS и основные шрифты прямо в страницы: превью-хостинги часто
// ограничивают загрузку отдельных стилей и шрифтов политикой безопасности (CSP).
const A = join(OUT, 'assets');
const FONT_INLINE = /(manrope|playfair-display)-(cyrillic|latin|latin-ext)-wght-normal\.[\w-]+\.woff2/;
const cssCache = new Map();
const jsCache = new Map();
const inlineCss = (name, prefix) => {
  if (!cssCache.has(name)) {
    let css = readFileSync(join(A, name), 'utf8');
    // Наборы шрифтов, которые не встраиваем (греческий, вьетнамский), убираем целиком
    css = css.replace(/@font-face\{[^}]*\}/g, (block) => {
      const m = block.match(/url\(\.\/([^)]+\.woff2)\)/);
      return m && !FONT_INLINE.test(m[1]) ? '' : block;
    });
    css = css.replace(/url\(\.\/([^)]+\.woff2)\)/g, (m, font) =>
      FONT_INLINE.test(font) ? `url(data:font/woff2;base64,${readFileSync(join(A, font)).toString('base64')})` : `url(__P__assets/${font})`,
    );
    cssCache.set(name, css);
  }
  return cssCache.get(name).replaceAll('__P__', prefix);
};
const inlineJs = (name) => {
  if (!jsCache.has(name)) {
    const r = buildSync({ entryPoints: [join(A, name)], bundle: true, format: 'esm', minify: true, write: false, logLevel: 'silent' });
    jsCache.set(name, r.outputFiles[0].text.replace(/<\/script/gi, '<\\/script'));
  }
  return jsCache.get(name);
};
for (const [f, prefix] of pending) {
  let h = readFileSync(f, 'utf8');
  h = h.replace(/<link rel="preload"[^>]*as="font"[^>]*>/g, '');
  h = h.replace(/<link rel="stylesheet" href="[^"]*assets\/([^"]+\.css)">/g, (_, n) => `<style>${inlineCss(n, prefix)}</style>`);
  h = h.replace(/<script type="module" src="[^"]*assets\/([^"]+\.js)"><\/script>/g, (_, n) => `<script type="module">${inlineJs(n)}</script>`);
  writeFileSync(f, h);
}
// Всё из assets теперь встроено в страницы
rmSync(A, { recursive: true, force: true });
console.log(`Готово: ${OUT}/ (${walk(OUT).length} файлов)`);
