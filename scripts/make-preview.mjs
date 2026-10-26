// Тестовая сборка для просмотра на любом статическом хостинге (в т.ч. превью по ссылке):
//  - формы в демо-режиме (PUBLIC_DEMO=true) — заявки никуда не отправляются;
//  - все абсолютные пути переписаны в относительные, ссылки на папки → index.html.
// Запуск: node scripts/make-preview.mjs → папка .preview/
import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync, readdirSync, statSync, rmSync, renameSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

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
    writeFileSync(f, h);
  } else if (f.endsWith('.css') || f.endsWith('.js')) {
    writeFileSync(f, readFileSync(f, 'utf8').replace(/url\(\/_astro\//g, 'url(./').replace(/\/_astro\//g, './'));
  }
}
console.log(`Готово: ${OUT}/ (${files.length} файлов)`);
