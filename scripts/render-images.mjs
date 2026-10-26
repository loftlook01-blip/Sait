// Рендер иллюстраций в WebP: node scripts/render-images.mjs
// Результат: public/images/art/<сцена>.webp (1600 px) и <сцена>-800.webp
// Чтобы заменить иллюстрацию фотографией — положите фото с тем же именем.
import sharp from 'sharp';
import { mkdirSync } from 'node:fs';
import { svg, VARIANTS } from './art/scenes.mjs';

const out = 'public/images/art';
mkdirSync(out, { recursive: true });
const jobs = [...VARIANTS.map((v) => [v, 'after']), ['before', 'before']];
for (const [name, state] of jobs) {
  const src = Buffer.from(svg(state === 'before' ? 'living' : name, state));
  const img = sharp(src, { density: 144 });
  await img.clone().resize(1600, 1200).webp({ quality: 82 }).toFile(`${out}/${name}.webp`);
  await img.clone().resize(800, 600).webp({ quality: 80 }).toFile(`${out}/${name}-800.webp`);
  console.log('✓', name);
}
