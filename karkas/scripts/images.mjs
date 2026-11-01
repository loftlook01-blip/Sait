// Рендеры PNG → WebP для сайта: node scripts/images.mjs <папка с PNG>
// <имя>.png → public/images/<имя>.webp (по ширине до 1600) и <имя>-800.webp
import sharp from 'sharp';
import { readdirSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const src = process.argv[2];
const out = 'public/images';
mkdirSync(out, { recursive: true });
for (const f of readdirSync(src).filter((f) => f.endsWith('.png'))) {
  const name = f.replace(/\.png$/, '');
  const img = sharp(join(src, f));
  const max = name === 'cozy' ? 2000 : 1600;
  await img.clone().resize({ width: max, withoutEnlargement: true }).webp({ quality: 80, effort: 6 }).toFile(`${out}/${name}.webp`);
  await img.clone().resize({ width: 800 }).webp({ quality: 76, effort: 6 }).toFile(`${out}/${name}-800.webp`);
  console.log('✓', name);
}
