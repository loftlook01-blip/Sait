/**
 * Сцены интерьеров и производства в виде SVG. Рендерятся в WebP скриптом scripts/render-images.mjs.
 * Координаты — 800×600, вывод — 1600×1200.
 */

const W = 800;
const H = 600;
const VP = { x: 400, y: 255 }; // точка схода
const BACK = { x1: 180, y1: 110, x2: 620, y2: 400 };

/** Псевдослучайность с зерном — чтобы картинки были детерминированными */
function rng(seed) {
  let s = seed;
  return () => ((s = (s * 16807) % 2147483647) - 1) / 2147483646;
}

const PALETTES = {
  raw: { ceil: '#cfccc6', back: '#bcb8b1', left: '#aaa69f', right: '#b3afa8', floor: ['#8f8a82', '#a29d95'], plank: false },
  warm: { ceil: '#f4f0ea', back: '#ece5d9', left: '#ddd3c4', right: '#e5ddd0', floor: ['#9a6c45', '#c79a6e'], plank: true },
  bath: { ceil: '#f1ede6', back: '#d8d0c4', left: '#c9c0b2', right: '#d1c8bb', floor: ['#ada193', '#cfc5b8'], plank: false },
  office: { ceil: '#2a2926', back: '#e7e3dc', left: '#d6d1c9', right: '#ddd8d0', floor: ['#8a867f', '#aaa69f'], plank: false },
  house: { ceil: '#e8dfd1', back: '#efe7db', left: '#e1d7c8', right: '#e8dfd2', floor: ['#7f532f', '#b07c4f'], plank: true },
  bedroom: { ceil: '#f4f0ea', back: '#e9e1d6', left: '#dcd2c4', right: '#e3dbcf', floor: ['#a37650', '#cfa57b'], plank: true },
};

function defs(id) {
  return `
  <filter id="${id}blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="${id}blur3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="${id}blur20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>
  <filter id="${id}grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" stitchTiles="stitch"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.55 0"/>
  </filter>
  <linearGradient id="${id}win" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3f7f8"/><stop offset="0.6" stop-color="#d8e3e7"/><stop offset="1" stop-color="#c3d2d8"/></linearGradient>
  <linearGradient id="${id}spill" x1="0" y1="0" x2="1" y2="0.7"><stop offset="0" stop-color="#fffaf0" stop-opacity="0.55"/><stop offset="1" stop-color="#fffaf0" stop-opacity="0"/></linearGradient>
  <linearGradient id="${id}aoFloor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0.28"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>
  <linearGradient id="${id}aoCeil" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0.10"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>
  <linearGradient id="${id}aoL" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0.14"/><stop offset="0.5" stop-color="#000" stop-opacity="0"/></linearGradient>
  <linearGradient id="${id}aoR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0.16"/><stop offset="0.5" stop-color="#000" stop-opacity="0"/></linearGradient>
  <radialGradient id="${id}glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffd9a8" stop-opacity="0.9"/><stop offset="0.4" stop-color="#ffd9a8" stop-opacity="0.35"/><stop offset="1" stop-color="#ffd9a8" stop-opacity="0"/></radialGradient>
  <radialGradient id="${id}vign" cx="0.5" cy="0.45" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.22"/></radialGradient>
  <linearGradient id="${id}oak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#b98a5f"/><stop offset="0.5" stop-color="#c9a077"/><stop offset="1" stop-color="#b3845a"/></linearGradient>
  <linearGradient id="${id}dark" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#23211d"/><stop offset="1" stop-color="#34302b"/></linearGradient>
  <linearGradient id="${id}fabric" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ddd3c4"/><stop offset="1" stop-color="#c3b6a3"/></linearGradient>
  <linearGradient id="${id}glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e6eef1" stop-opacity="0.65"/><stop offset="0.5" stop-color="#c9d7dc" stop-opacity="0.35"/><stop offset="1" stop-color="#e6eef1" stop-opacity="0.6"/></linearGradient>
  <pattern id="${id}grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#c98b5b" stroke-opacity="0.12"/></pattern>`;
}

const shadow = (id, cx, cy, rx, ry, o = 0.35) =>
  `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#000" opacity="${o}" filter="url(#${id}blur8)"/>`;
const glow = (id, cx, cy, r) => `<circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#${id}glow)"/>`;

/** Пол в перспективе: доски сходятся к точке схода, тон каждой доски чуть разный */
function floor(id, P, seed) {
  const r = rng(seed);
  const vx = (x) => VP.x + (x - VP.x) * ((BACK.y2 - VP.y) / (H - VP.y));
  let out = `<polygon points="0,600 800,600 620,400 180,400" fill="${P.floor[1]}"/>`;
  if (P.plank) {
    for (let x = -200; x < 1000; x += 46) {
      const t = 0.75 + r() * 0.5;
      out += `<polygon points="${x},600 ${x + 46},600 ${vx(x + 46)},400 ${vx(x)},400" fill="${P.floor[0]}" opacity="${(0.12 + r() * 0.22) * t}"/>`;
      out += `<line x1="${x}" y1="600" x2="${vx(x)}" y2="400" stroke="#3a2516" stroke-opacity="0.18" stroke-width="1"/>`;
    }
    // поперечные стыки досок
    for (let i = 0; i < 26; i++) {
      const y = 405 + r() * 190;
      const k = (y - VP.y) / (H - VP.y);
      const x = VP.x + (r() * 1200 - 600) * k;
      out += `<line x1="${x}" y1="${y}" x2="${x + 20 * k}" y2="${y}" stroke="#3a2516" stroke-opacity="0.2"/>`;
    }
  } else {
    // плитка / бетон: сетка
    for (let x = -400; x <= 1200; x += 100) out += `<line x1="${x}" y1="600" x2="${vx(x)}" y2="400" stroke="#000" stroke-opacity="0.06"/>`;
    for (const y of [420, 450, 495, 560]) {
      const k = (y - VP.y) / (H - VP.y);
      out += `<line x1="${VP.x - 700 * k}" y1="${y}" x2="${VP.x + 700 * k}" y2="${y}" stroke="#000" stroke-opacity="0.06"/>`;
    }
  }
  out += `<polygon points="0,600 800,600 620,400 180,400" fill="url(#${id}floorSheen)" opacity="0.6"/>`;
  return out;
}

function room(id, P, { seed = 1, raw = false, window = true } = {}) {
  return `
  <linearGradient id="${id}floorSheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0.18"/><stop offset="1" stop-color="#fff" stop-opacity="0.08"/></linearGradient>
  <polygon points="0,0 800,0 620,110 180,110" fill="${P.ceil}"/>
  <polygon points="0,0 180,110 180,400 0,600" fill="${P.left}"/>
  <polygon points="800,0 620,110 620,400 800,600" fill="${P.right}"/>
  <rect x="180" y="110" width="440" height="290" fill="${P.back}"/>
  ${floor(id, P, seed)}
  <!-- ambient occlusion по углам -->
  <rect x="180" y="330" width="440" height="70" fill="url(#${id}aoCeil)" transform="rotate(180 400 365)" opacity="0.8"/>
  <polygon points="180,400 620,400 680,445 120,445" fill="url(#${id}aoFloor)"/>
  <rect x="180" y="110" width="440" height="40" fill="url(#${id}aoCeil)" transform="rotate(180 400 130)"/>
  <rect x="180" y="110" width="90" height="290" fill="url(#${id}aoR)"/>
  <rect x="530" y="110" width="90" height="290" fill="url(#${id}aoL)"/>
  ${
    window
      ? `<polygon points="36,78 144,130 144,334 36,386" fill="#000" opacity="0.12" filter="url(#${id}blur3)"/>
  <polygon points="40,80 140,128 140,330 40,380" fill="url(#${id}win)" stroke="${raw ? '#8e8a83' : '#faf7f2'}" stroke-width="7"/>
  <line x1="90" y1="104" x2="90" y2="355" stroke="${raw ? '#8e8a83' : '#faf7f2'}" stroke-width="5"/>
  ${raw ? '' : `<polygon points="44,90 86,110 86,200 44,190" fill="#fff" opacity="0.35"/>`}
  <polygon points="140,330 40,380 330,600 640,600" fill="url(#${id}spill)"/>
  <polygon points="140,128 180,150 180,360 140,330" fill="url(#${id}spill)" opacity="0.6"/>`
      : ''
  }
  ${raw ? '' : `<line x1="180" y1="399" x2="620" y2="399" stroke="#fff" stroke-opacity="0.6" stroke-width="3"/>`}`;
}

function finish(id) {
  return `<rect width="800" height="600" fill="url(#${id}vign)"/><rect width="800" height="600" filter="url(#${id}grain)" opacity="0.07"/>`;
}

/* ───────────────────────── Сцены ───────────────────────── */

const S = {};

S.before = (id) => `
  ${room(id, PALETTES.raw, { raw: true, seed: 3 })}
  ${[230, 300, 370, 440, 510, 580].map((x) => `<line x1="${x}" y1="118" x2="${x}" y2="396" stroke="#8d8982" stroke-width="3"/>`).join('')}
  <path d="M260 160 h120 v40 h-120z M440 230 h80" stroke="#8d8982" stroke-width="2" fill="none" stroke-dasharray="6 6"/>
  <path d="M400 110 V170" stroke="#3a3632" stroke-width="2"/>
  ${glow(id, 400, 180, 70)}
  <circle cx="400" cy="178" r="9" fill="#fff4d6"/>
  <path d="M620 250 C 650 260, 700 230, 760 270" stroke="#c0392b" stroke-width="3" fill="none"/>
  <path d="M620 262 C 660 280, 690 250, 770 300" stroke="#e1b12c" stroke-width="3" fill="none"/>
  ${shadow(id, 565, 565, 70, 10, 0.4)}
  <g stroke="#6d6a64" stroke-width="7" stroke-linecap="round">
    <line x1="520" y1="560" x2="565" y2="330"/><line x1="610" y1="560" x2="565" y2="330"/>
    <line x1="530" y1="505" x2="598" y2="505"/><line x1="541" y1="450" x2="588" y2="450"/><line x1="552" y1="395" x2="578" y2="395"/>
  </g>
  ${shadow(id, 340, 585, 140, 12, 0.4)}
  <path d="M250 520 h70 l-8 62 h-54z" fill="#e5e1da"/><ellipse cx="285" cy="520" rx="35" ry="8" fill="#cfcac2"/>
  <rect x="330" y="540" width="110" height="46" rx="10" fill="#d8cfbd"/><rect x="350" y="515" width="100" height="40" rx="10" fill="#cdc3af"/>`;

S.living = (id) => `
  ${room(id, PALETTES.warm, { seed: 11 })}
  <!-- дубовые панели справа -->
  ${[0, 1, 2, 3, 4].map((i) => `<polygon points="${620 + i * 36},${110 - i * 22} ${655 + i * 36},${88 - i * 22} ${655 + i * 36},${422 + i * 22} ${620 + i * 36},${400 + i * 22}" fill="url(#${id}oak)" opacity="${i % 2 ? 0.92 : 1}"/><line x1="${655 + i * 36}" y1="${88 - i * 22}" x2="${655 + i * 36}" y2="${422 + i * 22}" stroke="#7b5534" stroke-opacity="0.35"/>`).join('')}
  <polygon points="620,110 800,0 800,600 620,400" fill="url(#${id}aoR)" opacity="0.7"/>
  <!-- картина -->
  ${shadow(id, 404, 206, 74, 54, 0.25)}
  <rect x="330" y="150" width="140" height="100" fill="#f8f4ec" stroke="#2a2723" stroke-width="5"/>
  <circle cx="400" cy="196" r="28" fill="#b6774b"/><rect x="368" y="212" width="64" height="22" fill="#2f4a43"/>
  <!-- диван -->
  ${shadow(id, 400, 418, 210, 14, 0.45)}
  <rect x="230" y="296" width="340" height="74" rx="20" fill="url(#${id}fabric)"/>
  <rect x="208" y="330" width="384" height="82" rx="24" fill="#c7baa7"/>
  <rect x="208" y="330" width="384" height="20" rx="10" fill="#fff" opacity="0.12"/>
  <rect x="248" y="318" width="146" height="42" rx="15" fill="#e5dccf"/><rect x="406" y="318" width="146" height="42" rx="15" fill="#e5dccf"/>
  <rect x="283" y="296" width="62" height="46" rx="11" fill="#2f4a43"/><rect x="455" y="300" width="56" height="42" rx="11" fill="#b6774b" opacity="0.9"/>
  <line x1="232" y1="412" x2="230" y2="426" stroke="#2a2723" stroke-width="5"/><line x1="568" y1="412" x2="570" y2="426" stroke="#2a2723" stroke-width="5"/>
  <!-- ковёр, столик -->
  <ellipse cx="400" cy="502" rx="268" ry="58" fill="#ebe3d6"/><ellipse cx="400" cy="502" rx="250" ry="50" fill="none" stroke="#d8cebd" stroke-width="2"/>
  ${shadow(id, 405, 522, 70, 10, 0.5)}
  <ellipse cx="400" cy="470" rx="96" ry="22" fill="#26231f"/><ellipse cx="392" cy="466" rx="70" ry="12" fill="#fff" opacity="0.07"/>
  <rect x="396" y="470" width="8" height="45" fill="#26231f"/><ellipse cx="400" cy="515" rx="40" ry="8" fill="#26231f"/>
  <rect x="362" y="446" width="30" height="18" rx="3" fill="#b6774b"/><circle cx="430" cy="456" r="9" fill="#f4efe7"/>
  <!-- подвесной светильник -->
  <line x1="470" y1="0" x2="470" y2="140" stroke="#2a2723" stroke-width="2"/>
  ${glow(id, 470, 180, 95)}
  <path d="M438 166 a32 28 0 0 1 64 0z" fill="#2a2723"/><ellipse cx="470" cy="166" rx="32" ry="5" fill="#fff1d6"/>
  <!-- растение -->
  ${shadow(id, 175, 502, 40, 7, 0.4)}
  <rect x="150" y="440" width="50" height="60" rx="6" fill="#f0e9dd"/><rect x="150" y="440" width="18" height="60" rx="6" fill="#000" opacity="0.06"/>
  <g stroke="#2f4a43" stroke-width="10" stroke-linecap="round" fill="none">
    <path d="M175 440 C 150 380, 120 360, 110 320"/><path d="M175 440 C 180 380, 200 340, 230 310"/><path d="M175 440 C 170 400, 160 360, 170 300"/>
  </g>
  <g stroke="#3e6157" stroke-width="5" stroke-linecap="round" fill="none"><path d="M175 440 C 190 400, 215 390, 240 370"/><path d="M175 440 C 150 410, 130 400, 120 380"/></g>`;

S.kitchen = (id) => `
  ${room(id, PALETTES.warm, { seed: 21 })}
  ${Array.from({ length: 9 }, (_, r) => Array.from({ length: 10 }, (_, c) => `<rect x="${180 + c * 48 + (r % 2 ? 24 : 0) - 24}" y="${112 + r * 18}" width="44" height="14" rx="1" fill="#b07c63" opacity="${0.25 + ((r * 7 + c * 3) % 5) * 0.05}"/>`).join('')).join('')}
  ${shadow(id, 325, 220, 130, 10, 0.3)}
  <rect x="200" y="140" width="250" height="70" fill="url(#${id}dark)"/>
  ${[283, 366].map((x) => `<line x1="${x}" y1="142" x2="${x}" y2="208" stroke="#4a453e" stroke-width="2"/>`).join('')}
  <rect x="200" y="210" width="250" height="4" fill="#ffe2b8"/>
  <polygon points="200,214 450,214 470,290 180,290" fill="#ffd9a8" opacity="0.18"/>
  <rect x="470" y="140" width="110" height="150" fill="#dcd7cf"/><rect x="484" y="156" width="82" height="52" rx="2" fill="#1b1916"/><rect x="484" y="156" width="82" height="10" fill="#fff" opacity="0.06"/>
  ${shadow(id, 400, 404, 210, 8, 0.4)}
  <rect x="200" y="288" width="400" height="16" fill="url(#${id}oak)"/>
  <rect x="200" y="304" width="400" height="96" fill="url(#${id}dark)"/>
  ${[280, 360, 440, 520].map((x) => `<line x1="${x}" y1="308" x2="${x}" y2="398" stroke="#4a453e" stroke-width="2"/>`).join('')}
  <rect x="300" y="282" width="60" height="6" fill="#9a968e"/><path d="M330 282 v-26 h14" stroke="#9a968e" stroke-width="4" fill="none"/>
  <!-- остров -->
  ${shadow(id, 400, 578, 170, 14, 0.5)}
  <rect x="250" y="428" width="300" height="24" fill="url(#${id}oak)"/><rect x="250" y="428" width="300" height="5" fill="#fff" opacity="0.18"/>
  <rect x="265" y="452" width="270" height="112" fill="url(#${id}dark)"/>
  ${[300, 500].map((x) => `${shadow(id, x, 588, 34, 6, 0.4)}<rect x="${x - 22}" y="470" width="44" height="10" rx="3" fill="#b6774b"/><line x1="${x - 15}" y1="480" x2="${x - 22}" y2="590" stroke="#1d1b18" stroke-width="4"/><line x1="${x + 15}" y1="480" x2="${x + 22}" y2="590" stroke="#1d1b18" stroke-width="4"/>`).join('')}
  <!-- подвесы -->
  ${[330, 400, 470].map((x) => `<line x1="${x}" y1="0" x2="${x}" y2="300" stroke="#1d1b18" stroke-width="2"/>${glow(id, x, 330, 60)}<path d="M${x - 16} 318 a16 18 0 0 1 32 0z" fill="#1d1b18"/><circle cx="${x}" cy="320" r="5" fill="#fff4dc"/>`).join('')}
  <polygon points="300,440 500,440 520,452 280,452" fill="#ffd9a8" opacity="0.25"/>
  <!-- лофт-перегородка -->
  <polygon points="640,98 760,24 760,576 640,412" fill="url(#${id}glass)"/>
  <polygon points="650,110 700,80 700,250 650,270" fill="#fff" opacity="0.25"/>
  <g stroke="#15130f" stroke-width="7" fill="none"><polygon points="640,98 760,24 760,576 640,412"/></g>
  ${[0.25, 0.5, 0.75].map((t) => `<line x1="640" y1="${98 + 314 * t}" x2="760" y2="${24 + 552 * t}" stroke="#15130f" stroke-width="5"/>`).join('')}
  <line x1="700" y1="61" x2="700" y2="494" stroke="#15130f" stroke-width="5"/>`;

S.bath = (id) => `
  ${room(id, PALETTES.bath, { seed: 31 })}
  <rect x="180" y="110" width="440" height="290" fill="#cfc6b8" opacity="0.25"/>
  ${Array.from({ length: 40 }, (_, i) => `<ellipse cx="${200 + ((i * 97) % 410)}" cy="${125 + ((i * 53) % 260)}" rx="${20 + (i % 4) * 12}" ry="${8 + (i % 3) * 5}" fill="#fff" opacity="0.05"/>`).join('')}
  <!-- ниша -->
  <rect x="470" y="170" width="110" height="70" fill="#b9ae9f"/><rect x="470" y="170" width="110" height="18" fill="#000" opacity="0.08"/>
  <rect x="470" y="170" width="110" height="4" fill="#ffe2b8"/><polygon points="470,174 580,174 575,232 475,232" fill="#ffd9a8" opacity="0.25"/>
  <rect x="470" y="232" width="110" height="10" fill="url(#${id}oak)"/>
  <rect x="490" y="196" width="18" height="36" rx="4" fill="#2f4a43"/><rect x="518" y="208" width="14" height="24" rx="4" fill="#f4efe7"/><rect x="542" y="214" width="22" height="18" rx="3" fill="#b6774b"/>
  <!-- зеркало с подсветкой -->
  ${glow(id, 300, 200, 90)}
  <circle cx="300" cy="200" r="58" fill="#dfe8ea" stroke="#2a2723" stroke-width="4"/><path d="M262 172 a50 50 0 0 1 40 -26" stroke="#fff" stroke-width="6" opacity="0.6" fill="none" stroke-linecap="round"/>
  ${shadow(id, 300, 338, 70, 6, 0.35)}
  <rect x="235" y="290" width="130" height="40" fill="url(#${id}oak)"/><ellipse cx="300" cy="290" rx="42" ry="8" fill="#f8f5ef"/>
  <path d="M300 266 v16 h10" stroke="#2a2723" stroke-width="4" fill="none"/>
  <!-- ванна -->
  ${shadow(id, 415, 545, 170, 14, 0.45)}
  <path d="M250 430 h330 c0 70 -40 110 -110 110 h-110 c-70 0 -110 -40 -110 -110z" fill="#faf8f4"/>
  <path d="M250 430 h70 c0 70 20 100 60 110 h-20 c-70 0 -110 -40 -110 -110z" fill="#000" opacity="0.05"/>
  <ellipse cx="415" cy="430" rx="165" ry="18" fill="#e7e1d7"/><ellipse cx="415" cy="433" rx="150" ry="12" fill="#d4e2e6"/>
  <path d="M570 430 v-80 h-30" stroke="#2a2723" stroke-width="5" fill="none"/>
  <!-- полотенцесушитель RAL -->
  <g stroke="#2f4a43" stroke-width="6"><line x1="660" y1="150" x2="660" y2="360"/><line x1="720" y1="130" x2="720" y2="390"/>${[180, 230, 280, 330].map((y) => `<line x1="660" y1="${y}" x2="720" y2="${y - 12}"/>`).join('')}</g>
  <rect x="665" y="220" width="50" height="90" fill="#ebe3d6"/><rect x="665" y="220" width="12" height="90" fill="#000" opacity="0.06"/>`;

S.bedroom = (id) => `
  ${room(id, PALETTES.bedroom, { seed: 41 })}
  ${Array.from({ length: 11 }, (_, i) => `<rect x="${190 + i * 39}" y="168" width="35" height="164" rx="11" fill="#cdbfae"/><rect x="${190 + i * 39}" y="168" width="12" height="164" rx="6" fill="#fff" opacity="0.18"/>`).join('')}
  ${[215, 585].map((x) => `${glow(id, x, 205, 70)}<circle cx="${x}" cy="200" r="10" fill="#2a2723"/><circle cx="${x}" cy="203" r="4" fill="#fff4dc"/>`).join('')}
  ${shadow(id, 415, 498, 240, 14, 0.5)}
  <rect x="260" y="298" width="280" height="42" rx="10" fill="#f6f2ea"/>
  <rect x="290" y="282" width="100" height="32" rx="11" fill="#fcfaf6"/><rect x="410" y="282" width="100" height="32" rx="11" fill="#fcfaf6"/>
  <polygon points="240,340 560,340 610,470 190,470" fill="#e7ddcf"/>
  <polygon points="300,368 600,368 640,470 250,470" fill="#2f4a43" opacity="0.9"/>
  <path d="M250 470 Q 320 440 420 452 T 640 470" fill="#3d5d55" opacity="0.6"/>
  <rect x="190" y="470" width="450" height="30" fill="url(#${id}oak)"/>
  ${shadow(id, 215, 402, 36, 5, 0.4)}${shadow(id, 585, 402, 36, 5, 0.4)}
  <rect x="185" y="330" width="60" height="70" fill="url(#${id}oak)"/><rect x="555" y="330" width="60" height="70" fill="url(#${id}oak)"/>
  <line x1="185" y1="365" x2="245" y2="365" stroke="#7b5534" stroke-opacity="0.4"/><line x1="555" y1="365" x2="615" y2="365" stroke="#7b5534" stroke-opacity="0.4"/>
  <polygon points="18,40 62,60 72,420 12,450" fill="#d8cdbd"/>${[25, 40, 55].map((x) => `<line x1="${x}" y1="${45 + (x - 18) / 2}" x2="${x}" y2="${440 - (x - 18) / 2}" stroke="#000" stroke-opacity="0.06" stroke-width="5"/>`).join('')}
  <polygon points="128,110 160,125 165,350 122,372" fill="#d8cdbd"/>
  <polygon points="640,98 792,6 792,594 640,412" fill="#ebe3d6"/>
  <line x1="716" y1="52" x2="716" y2="503" stroke="#cbbfae" stroke-width="3"/>
  <line x1="700" y1="250" x2="700" y2="320" stroke="#b6774b" stroke-width="4"/><line x1="732" y1="240" x2="732" y2="320" stroke="#b6774b" stroke-width="4"/>`;

S.office = (id) => `
  ${room(id, PALETTES.office, { seed: 51 })}
  ${[0.2, 0.45, 0.7].map((t) => `${glow(id, 260 + 200 * t, 35 + 60 * t, 70)}<rect x="${200 + 200 * t}" y="${30 + 60 * t}" width="120" height="10" rx="5" fill="#ffe2b8"/>`).join('')}
  ${shadow(id, 400, 404, 210, 8, 0.35)}
  <rect x="200" y="130" width="400" height="270" fill="url(#${id}glass)"/>
  <polygon points="210,140 280,140 230,390 210,390" fill="#fff" opacity="0.18"/>
  <rect x="200" y="130" width="400" height="270" fill="none" stroke="#15130f" stroke-width="7"/>
  ${[300, 400, 500].map((x) => `<line x1="${x}" y1="130" x2="${x}" y2="400" stroke="#15130f" stroke-width="5"/>`).join('')}
  <rect x="260" y="290" width="280" height="14" fill="url(#${id}oak)"/>
  ${[280, 340, 400, 460, 520].map((x) => `<rect x="${x - 14}" y="304" width="28" height="40" rx="6" fill="#2f4a43"/>`).join('')}
  <rect x="350" y="168" width="100" height="70" fill="#f7f3ec" stroke="#15130f" stroke-width="3"/>
  <polyline points="362,220 384,200 404,212 436,184" stroke="#b6774b" stroke-width="4" fill="none"/>
  ${shadow(id, 400, 594, 260, 10, 0.5)}
  <rect x="150" y="468" width="500" height="20" fill="url(#${id}oak)"/><rect x="150" y="468" width="500" height="4" fill="#fff" opacity="0.2"/>
  <line x1="180" y1="488" x2="180" y2="592" stroke="#15130f" stroke-width="6"/><line x1="620" y1="488" x2="620" y2="592" stroke="#15130f" stroke-width="6"/>
  ${[260, 400, 540].map((x) => `<rect x="${x - 42}" y="418" width="84" height="52" rx="4" fill="#15130f"/><rect x="${x - 38}" y="422" width="76" height="40" rx="2" fill="#2c3a40"/><rect x="${x - 38}" y="422" width="76" height="12" fill="#fff" opacity="0.06"/>`).join('')}
  ${shadow(id, 690, 502, 44, 6, 0.4)}
  <rect x="660" y="430" width="60" height="70" fill="#15130f"/><circle cx="690" cy="398" r="46" fill="#2f4a43"/><circle cx="676" cy="384" r="24" fill="#3e6157"/>`;

S.house = (id) => `
  ${room(id, PALETTES.house, { seed: 61 })}
  ${[0.25, 0.5, 0.75].map((t) => `<polygon points="${800 * t - 30},0 ${800 * t + 30},0 ${180 + 440 * t + 8},110 ${180 + 440 * t - 8},110" fill="#7f532f"/><polygon points="${800 * t - 30},0 ${800 * t - 10},0 ${180 + 440 * t - 2},110 ${180 + 440 * t - 8},110" fill="#000" opacity="0.15"/>`).join('')}
  <rect x="180" y="104" width="440" height="10" fill="#7f532f"/>
  ${Array.from({ length: 10 }, (_, i) => `<rect x="180" y="${118 + i * 28}" width="440" height="3" fill="#c6b498" opacity="0.8"/><rect x="180" y="${121 + i * 28}" width="440" height="8" fill="#fff" opacity="0.08"/>`).join('')}
  <!-- камин -->
  ${shadow(id, 295, 404, 90, 8, 0.4)}
  <rect x="220" y="250" width="150" height="150" fill="url(#${id}dark)"/><rect x="214" y="244" width="162" height="10" fill="#4a453e"/>
  <rect x="245" y="300" width="100" height="70" fill="#141210"/>
  ${glow(id, 295, 345, 80)}
  <path d="M276 368 q12 -42 20 -54 q16 24 10 54z" fill="#f0a35e"/><path d="M288 368 q6 -22 10 -28 q8 14 4 28z" fill="#ffe0a8"/>
  <!-- лестница на косоуре -->
  ${shadow(id, 470, 404, 70, 6, 0.4)}
  <line x1="420" y1="400" x2="610" y2="140" stroke="#15130f" stroke-width="11"/>
  ${Array.from({ length: 9 }, (_, i) => `<rect x="${402 + i * 21}" y="${386 - i * 29}" width="62" height="10" fill="#b07c4f"/><rect x="${402 + i * 21}" y="${394 - i * 29}" width="62" height="3" fill="#000" opacity="0.2"/>`).join('')}
  <line x1="440" y1="340" x2="630" y2="80" stroke="#15130f" stroke-width="4"/>
  ${Array.from({ length: 7 }, (_, i) => `<line x1="${450 + i * 27}" y1="${326 - i * 37}" x2="${450 + i * 27}" y2="${386 - i * 37}" stroke="#15130f" stroke-width="3"/>`).join('')}
  <!-- кресло и ковёр -->
  <ellipse cx="420" cy="540" rx="210" ry="42" fill="#ebe3d6" opacity="0.75"/>
  ${shadow(id, 225, 534, 80, 8, 0.5)}
  <rect x="150" y="440" width="150" height="90" rx="20" fill="#2f4a43"/><rect x="165" y="420" width="120" height="52" rx="16" fill="#3b5a51"/><rect x="165" y="420" width="120" height="14" rx="7" fill="#fff" opacity="0.1"/>`;

S.blueprint = (id) => `
  <rect width="800" height="600" fill="#1f1d19"/><rect width="800" height="600" fill="url(#${id}grid)"/>
  <g fill="none" stroke="#efe6d8" stroke-width="6" stroke-linejoin="round">
    <path d="M120 100 H680 V500 H120 Z"/>
    <path d="M380 100 V260 M380 330 V500 M120 300 H300 M350 300 H380 M520 100 V200 M520 260 V320 H680"/>
  </g>
  <g fill="none" stroke="#c98b5b" stroke-width="2.5">
    <rect x="420" y="360" width="200" height="80" rx="12"/><rect x="450" y="380" width="60" height="40" rx="6"/>
    <rect x="160" y="140" width="150" height="110" rx="8"/><path d="M160 170 H310"/>
    <rect x="560" y="130" width="90" height="40"/><circle cx="600" cy="230" r="22"/>
    <rect x="150" y="360" width="200" height="30"/><rect x="150" y="430" width="70" height="40"/>
    <path d="M380 260 a70 70 0 0 1 70 70" stroke-dasharray="6 6"/><path d="M300 300 a50 50 0 0 0 50 -50" stroke-dasharray="6 6"/>
  </g>
  <g stroke="#efe6d8" stroke-opacity="0.6" stroke-width="1.5">
    <line x1="120" y1="70" x2="680" y2="70"/><line x1="120" y1="62" x2="120" y2="78"/><line x1="680" y1="62" x2="680" y2="78"/>
    <line x1="710" y1="100" x2="710" y2="500"/><line x1="702" y1="100" x2="718" y2="100"/><line x1="702" y1="500" x2="718" y2="500"/>
  </g>
  <g fill="#efe6d8" font-family="DejaVu Sans Mono" font-size="15">
    <text x="372" y="60">11 200</text><text x="722" y="285" transform="rotate(90 722 285)">8 000</text>
    <text x="160" y="285" fill="#c98b5b">Спальня 16,4 м²</text><text x="440" y="478" fill="#c98b5b">Гостиная 28,1 м²</text>
    <text x="535" y="300" fill="#c98b5b" font-size="12">С/у 5,2</text><text x="160" y="345" fill="#c98b5b">Кухня 12,7 м²</text>
  </g>
  <g transform="translate(560 520)" font-family="DejaVu Sans Mono" font-size="11" fill="#a59d92"><rect x="0" y="0" width="200" height="56" fill="none" stroke="#a59d92"/><text x="10" y="20">ЛИСТ 04 · ПЛАН МЕБЕЛИ</text><text x="10" y="40">М 1:50 · АР-04</text></g>`;

function workshopBase(id) {
  return `
  <rect width="800" height="600" fill="#211f1b"/>
  <rect x="0" y="0" width="800" height="420" fill="#2a2723"/>
  <polygon points="0,420 800,420 800,600 0,600" fill="#33302a"/>
  ${Array.from({ length: 9 }, (_, i) => `<line x1="${i * 100}" y1="420" x2="${400 + (i * 100 - 400) * 2}" y2="600" stroke="#000" stroke-opacity="0.15"/>`).join('')}
  <g stroke="#3e3a34" stroke-width="5" fill="none"><path d="M0 60 H800 M0 120 H800"/>${Array.from({ length: 10 }, (_, i) => `<path d="M${i * 80} 60 L${i * 80 + 40} 120 L${i * 80 + 80} 60"/>`).join('')}</g>
  ${[160, 400, 640].map((x) => `<rect x="${x - 50}" y="128" width="100" height="8" fill="#f6ead2"/><polygon points="${x - 50},136 ${x + 50},136 ${x + 150},420 ${x - 150},420" fill="#f6ead2" opacity="0.06"/><ellipse cx="${x}" cy="430" rx="160" ry="22" fill="#f6ead2" opacity="0.05"/>`).join('')}
  <rect x="0" y="180" width="800" height="6" fill="#b6774b" opacity="0.5"/>`;
}

S['workshop-wood'] = (id) => `
  ${workshopBase(id)}
  ${shadow(id, 185, 382, 130, 10, 0.5)}
  ${Array.from({ length: 7 }, (_, i) => `<rect x="70" y="${358 - i * 22}" width="230" height="18" fill="${i % 2 ? '#d6b890' : '#c6a27b'}"/><rect x="70" y="${358 - i * 22}" width="230" height="3" fill="#fff" opacity="0.18"/><rect x="70" y="${358 - i * 22}" width="4" height="18" fill="#efe1c8"/>`).join('')}
  ${[0, 1, 2].map((i) => `<rect x="${110 + i * 80}" y="196" width="60" height="120" fill="url(#${id}oak)" stroke="#e2c49c" stroke-width="3"/>`).join('')}
  ${shadow(id, 530, 528, 210, 12, 0.55)}
  <rect x="340" y="378" width="380" height="26" fill="#dad5cb"/><rect x="340" y="378" width="380" height="5" fill="#fff" opacity="0.3"/>
  <rect x="360" y="404" width="40" height="122" fill="#4a463f"/><rect x="660" y="404" width="40" height="122" fill="#4a463f"/>
  <rect x="400" y="348" width="260" height="30" fill="#e6c9a0"/><rect x="400" y="348" width="260" height="5" fill="#fff" opacity="0.3"/>
  <circle cx="560" cy="378" r="40" fill="none" stroke="#b6774b" stroke-width="5" stroke-dasharray="6 5"/>
  <rect x="540" y="250" width="40" height="92" fill="#b6774b"/><rect x="520" y="230" width="80" height="24" fill="#3e3a34"/>
  ${glow(id, 560, 345, 50)}
  ${Array.from({ length: 40 }, (_, i) => `<circle cx="${590 + ((i * 37) % 140)}" cy="${340 - ((i * 23) % 80)}" r="${1.2 + (i % 3)}" fill="#ecd3ab" opacity="${0.5 + (i % 4) * 0.12}"/>`).join('')}
  <rect x="600" y="300" width="140" height="10" fill="#000" opacity="0"/>`;

S['workshop-metal'] = (id) => `
  ${workshopBase(id)}
  ${shadow(id, 410, 534, 230, 12, 0.55)}
  <rect x="200" y="398" width="420" height="22" fill="#5b5750"/><rect x="200" y="398" width="420" height="4" fill="#fff" opacity="0.2"/>
  <rect x="220" y="420" width="20" height="110" fill="#3a3631"/><rect x="580" y="420" width="20" height="110" fill="#3a3631"/>
  <g stroke="#9e9a92" stroke-width="10" fill="none"><rect x="260" y="230" width="300" height="170"/><line x1="410" y1="230" x2="410" y2="400"/><line x1="260" y1="315" x2="560" y2="315"/></g>
  <g stroke="#c9c5bd" stroke-width="2" fill="none" opacity="0.5"><rect x="256" y="226" width="300" height="170"/></g>
  <circle cx="410" cy="315" r="160" fill="#ffb15e" opacity="0.10" filter="url(#${id}blur20)"/>
  <circle cx="410" cy="315" r="70" fill="#ffc77a" opacity="0.30" filter="url(#${id}blur8)"/>
  <circle cx="410" cy="315" r="14" fill="#fffaf0"/>
  ${Array.from({ length: 34 }, (_, i) => { const a = (i / 34) * Math.PI * 2; const r = 40 + ((i * 17) % 90); return `<line x1="${410 + Math.cos(a) * 18}" y1="${315 + Math.sin(a) * 18}" x2="${410 + Math.cos(a) * r}" y2="${315 + Math.sin(a) * r + 26}" stroke="#ffcf80" stroke-width="${1.5 + (i % 3)}" stroke-linecap="round" opacity="${0.6 + (i % 3) * 0.15}"/>`; }).join('')}
  ${[0, 1, 2, 3].map((i) => `<rect x="660" y="${200 + i * 30}" width="120" height="10" fill="#7d7972"/><rect x="660" y="${200 + i * 30}" width="120" height="3" fill="#fff" opacity="0.2"/>`).join('')}
  <path d="M120 420 l30 -150 l40 0 l10 150z" fill="#3e3a34"/><rect x="128" y="300" width="64" height="40" rx="4" fill="#b6774b"/>`;

S['workshop-powder'] = (id) => `
  ${workshopBase(id)}
  ${shadow(id, 400, 478, 260, 10, 0.5)}
  <rect x="150" y="150" width="500" height="320" fill="#2f2c27" stroke="#4a463f" stroke-width="6"/>
  <rect x="170" y="170" width="460" height="280" fill="#3b3833"/>
  <rect x="170" y="170" width="460" height="40" fill="#fff" opacity="0.04"/>
  <line x1="170" y1="200" x2="630" y2="200" stroke="#8a867f" stroke-width="5"/>
  ${[['#1d1b18', 210], ['#b6774b', 320], ['#2f4a43', 430], ['#ebe6de', 540]].map(([c, x]) => `<line x1="${x}" y1="200" x2="${x}" y2="240" stroke="#9a968e" stroke-width="2"/><rect x="${x - 35}" y="240" width="70" height="150" fill="${c}"/><rect x="${x - 35}" y="240" width="14" height="150" fill="#fff" opacity="0.12"/>`).join('')}
  <ellipse cx="480" cy="330" rx="140" ry="70" fill="#c88a5c" opacity="0.22" filter="url(#${id}blur20)"/>
  ${Array.from({ length: 70 }, (_, i) => `<circle cx="${370 + ((i * 41) % 230)}" cy="${280 + ((i * 29) % 110)}" r="${1 + (i % 3) * 0.8}" fill="#e0a77a" opacity="${0.4 + (i % 4) * 0.12}"/>`).join('')}
  <path d="M650 362 l-84 -18 l6 -16 l88 14z" fill="#d7d2c8"/><rect x="650" y="358" width="16" height="52" fill="#9a968e" transform="rotate(10 650 358)"/>
  ${['#1d1b18', '#3b3833', '#b6774b', '#c49a70', '#2f4a43', '#ebe6de', '#7a8b8f', '#8e3b2e'].map((c, i) => `<rect x="${150 + i * 40}" y="500" width="34" height="34" rx="3" fill="${c}"/>`).join('')}
  <text x="150" y="560" font-family="DejaVu Sans" font-size="12" fill="#a59d92">RAL 9005 · 7022 · 8023 · 1011 · 6004 · 9001</text>`;

S.hall = (id) => `
  ${room(id, PALETTES.warm, { seed: 71, window: false })}
  <!-- скрытая дверь и шкаф -->
  ${shadow(id, 300, 402, 120, 6, 0.35)}
  <rect x="200" y="130" width="200" height="270" fill="#e2d9cb"/>
  ${[250, 300, 350].map((x) => `<line x1="${x}" y1="130" x2="${x}" y2="400" stroke="#cbbfae" stroke-width="2"/>`).join('')}
  <rect x="420" y="130" width="90" height="270" fill="#ece5d9"/><rect x="418" y="128" width="94" height="274" fill="none" stroke="#2a2723" stroke-opacity="0.18" stroke-width="2"/>
  <line x1="498" y1="260" x2="498" y2="300" stroke="#b6774b" stroke-width="3"/>
  <!-- зеркало и банкетка -->
  ${glow(id, 565, 240, 70)}
  <rect x="530" y="150" width="70" height="170" rx="35" fill="#dfe8ea" stroke="#2a2723" stroke-width="3"/>
  ${shadow(id, 300, 470, 110, 8, 0.45)}
  <rect x="200" y="430" width="200" height="36" rx="8" fill="#b6774b"/><rect x="200" y="430" width="200" height="8" rx="4" fill="#fff" opacity="0.15"/>
  <line x1="215" y1="466" x2="212" y2="478" stroke="#15130f" stroke-width="4"/><line x1="385" y1="466" x2="388" y2="478" stroke="#15130f" stroke-width="4"/>
  <!-- вешалка из металла -->
  <g stroke="#15130f" stroke-width="5"><line x1="660" y1="90" x2="660" y2="470"/><line x1="660" y1="140" x2="720" y2="110"/><line x1="660" y1="140" x2="600" y2="110"/></g>
  <path d="M700 120 q20 60 0 140 h-30 q-14 -70 6 -140z" fill="#2f4a43"/>
  ${[0.2, 0.5, 0.8].map((t) => `${glow(id, 220 + 360 * t, 30 + 60 * t, 50)}<circle cx="${220 + 360 * t}" cy="${30 + 60 * t}" r="6" fill="#fff1d6"/>`).join('')}`;

export const VARIANTS = ['living', 'kitchen', 'bath', 'bedroom', 'office', 'house', 'hall', 'blueprint', 'workshop-wood', 'workshop-metal', 'workshop-powder'];

/** Сцена «до»: та же комната в черновой отделке */
export function svg(variant, state = 'after') {
  const id = `s${variant.replace(/\W/g, '')}${state}`;
  const body = state === 'before' ? S.before(id) : S[variant](id);
  const grain = variant === 'blueprint' ? '' : finish(id);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="1600" height="1200"><defs>${defs(id)}</defs>${body}${grain}</svg>`;
}
