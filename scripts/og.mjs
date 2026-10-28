// Генерация OG-картинки и PNG-иконок: node scripts/og.mjs
import sharp from 'sharp';
import { readFileSync, existsSync } from 'node:fs';

const fav = readFileSync('public/favicon.svg');
await sharp(fav, { density: 1200 }).resize(180, 180).png().toFile('public/apple-touch-icon.png');
await sharp(fav, { density: 1200 }).resize(512, 512).png().toFile('public/icon-512.png');

const brand = process.argv[2] || 'Северная мастерская';
const og = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#1f1d19"/>
  <g stroke="#c98b5b" stroke-opacity="0.12">${Array.from({ length: 31 }, (_, i) => `<path d="M${i * 40} 0V630"/>`).join('')}${Array.from({ length: 16 }, (_, i) => `<path d="M0 ${i * 40}H1200"/>`).join('')}</g>
  <g fill="none" stroke="#efe6d8" stroke-opacity="0.35" stroke-width="4"><path d="M880 120H1120V510H880Z M1000 120V280 M1000 340V510 M880 320H960"/></g>
  <g fill="none" stroke="#c98b5b" stroke-width="2.5" stroke-opacity="0.8"><rect x="1020" y="390" width="80" height="80" rx="10"/><rect x="900" y="150" width="80" height="70" rx="6"/></g>
  <rect x="80" y="90" width="64" height="64" rx="18" fill="#f4f1ec"/>
  <path d="M96 138V120l16-11 16 11v18" fill="none" stroke="#15130f" stroke-width="3.5" stroke-linejoin="round"/>
  <path d="M106 138v-11h12v11" fill="none" stroke="#b6774b" stroke-width="3.5" stroke-linejoin="round"/>
  <text x="164" y="134" font-family="Georgia, serif" font-size="34" fill="#f4f1ec">${brand}</text>
  <text x="80" y="300" font-family="Georgia, serif" font-size="74" fill="#f4f1ec">Ремонт под ключ</text>
  <text x="80" y="385" font-family="Georgia, serif" font-size="74" font-style="italic" fill="#b6774b">в Архангельске</text>
  <text x="80" y="470" font-family="Arial, sans-serif" font-size="26" fill="#a59d92">Дизайн-проект · Фиксированная смета · Собственный цех</text>
  <text x="80" y="540" font-family="Arial, sans-serif" font-size="24" fill="#a59d92">Столярное и сварочное производство · Порошковая покраска</text>
</svg>`;
// Если есть фотореалистичный рендер — кладём его фоном справа, текст на тёмном градиенте слева
const hero = 'public/images/art/hero.webp';
if (existsSync(hero)) {
  const bg = await sharp(hero).resize(1200, 630, { fit: 'cover', position: 'right' }).toBuffer();
  const shade = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"><defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#15130f" stop-opacity="0.94"/><stop offset="0.5" stop-color="#15130f" stop-opacity="0.78"/><stop offset="0.85" stop-color="#15130f" stop-opacity="0.1"/></linearGradient></defs><rect width="1200" height="630" fill="url(#g)"/></svg>`;
  const text = og.replace(/<rect width="1200" height="630" fill="#1f1d19"\/>[\s\S]*?<rect x="80"/, '<rect x="80"');
  await sharp(bg)
    .composite([{ input: Buffer.from(shade) }, { input: Buffer.from(text) }])
    .jpeg({ quality: 86 })
    .toFile('public/og.jpg');
} else {
  await sharp(Buffer.from(og)).jpeg({ quality: 88 }).toFile('public/og.jpg');
}
console.log('OK: og.jpg, apple-touch-icon.png, icon-512.png');
