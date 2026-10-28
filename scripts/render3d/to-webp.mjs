// Конвертация рендеров в WebP для сайта: node scripts/render3d/to-webp.mjs <папка с PNG>
// Сцена → <имя>.webp (полный размер) и <имя>-800.webp; hero → hero.webp (1920) и hero-1200.webp
import sharp from 'sharp';
import { readdirSync } from 'node:fs';
import { join } from 'node:path';

const src = process.argv[2];
const out = 'public/images/art';
for (const f of readdirSync(src).filter((f) => f.endsWith('.png'))) {
  const name = f.replace(/\.png$/, '');
  const img = sharp(join(src, f));
  if (name === 'hero') {
    await img.clone().webp({ quality: 80 }).toFile(`${out}/hero.webp`);
    await img.clone().resize(1200).webp({ quality: 78 }).toFile(`${out}/hero-1200.webp`);
  } else if (name.startsWith('var-')) {
    await img.clone().webp({ quality: 80 }).toFile(`${out}/${name}.webp`);
  } else {
    await img.clone().webp({ quality: 80 }).toFile(`${out}/${name}.webp`);
    await img.clone().resize(800).webp({ quality: 78 }).toFile(`${out}/${name}-800.webp`);
  }
  console.log('✓', name);
}
