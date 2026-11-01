// Картинка для соцсетей и мессенджеров 1200×630 + иконки: node scripts/og.mjs
import sharp from 'sharp';
import { writeFileSync } from 'node:fs';

const brand = 'КАРКАС';
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
  <defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#1a3e38" stop-opacity="0.96"/><stop offset="0.55" stop-color="#1a3e38" stop-opacity="0.85"/><stop offset="1" stop-color="#1a3e38" stop-opacity="0"/></linearGradient></defs>
  <rect width="1200" height="630" fill="url(#g)"/>
  <g fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round" transform="translate(72 72) scale(1.6)"><path d="M4 28V13L16 4l12 9v15"/><path d="M11 28V18h10v10"/></g>
  <text x="140" y="112" font-family="Onest, Arial, sans-serif" font-weight="800" font-size="40" fill="#fff" letter-spacing="2">${brand}</text>
  <text x="72" y="300" font-family="Onest, Arial, sans-serif" font-weight="800" font-size="64" fill="#fff">МОДУЛЬНЫЕ ДОМА</text>
  <text x="72" y="376" font-family="Onest, Arial, sans-serif" font-weight="800" font-size="64" fill="#fff">ПОД КЛЮЧ ЗА 45 ДНЕЙ</text>
  <text x="72" y="446" font-family="Onest, Arial, sans-serif" font-size="30" fill="#d9e6e2">от 1,69 млн ₽ · ипотека 3–6% · гарантия 5 лет</text>
  <rect x="72" y="500" width="340" height="64" rx="14" fill="#d9a35f"/>
  <text x="242" y="542" text-anchor="middle" font-family="Onest, Arial, sans-serif" font-weight="700" font-size="26" fill="#1a3e38">Архангельск и область</text>
</svg>`;
const bg = await sharp('public/images/hero.webp').resize(1200, 630, { fit: 'cover', position: 'centre' }).toBuffer();
await sharp(bg).composite([{ input: Buffer.from(svg) }]).jpeg({ quality: 84, mozjpeg: true }).toFile('public/og.jpg');

const fav = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#24514a"/><g fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round" transform="translate(8 8) scale(1.5)"><path d="M4 28V13L16 4l12 9v15"/><path d="M11 28V18h10v10"/></g></svg>`;
writeFileSync('public/favicon.svg', fav);
await sharp(Buffer.from(fav)).resize(180, 180).png().toFile('public/apple-touch-icon.png');
await sharp(Buffer.from(fav)).resize(512, 512).png().toFile('public/icon-512.png');
console.log('✓ og.jpg, favicon.svg, apple-touch-icon.png, icon-512.png');
