#!/usr/bin/env python3
"""
Генерация иллюстрации (Gemini-совместимый API, модель nano-banana — как в scripts/gen-images.py сайта).

  python3 scripts/gen_image.py "промпт на английском" data/images/out.jpg [--ref фото.jpg] [--aspect 4:5]

.env: IMG_API_KEY, IMG_API_URL (по умолчанию api-market1.shop … nano-banana-2.1:generateContent).

ПРАВИЛО: сгенерированное изображение — только «идея/концепт/визуализация». Не выдавать за выполненную работу.
"""
import argparse, base64, json, os, re, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import vk  # noqa: F401,E402  (подгружает .env)

URL = os.environ.get('IMG_API_URL', 'https://api-market1.shop/v1beta/models/nano-banana-2.1:generateContent')
STYLE = (" Realistic photo for a Russian furniture workshop's social media: natural soft northern daylight, true-to-life colours, "
         "real materials with small imperfections, solid wood grain clearly visible, powder-coated steel with fine texture. "
         "Not a 3D render, not staged luxury. No people's faces, no text, no logos, no watermarks.")
ASPECT = {'4:5': 'Vertical 4:5 portrait frame.', '1:1': 'Square frame.', '9:16': 'Tall vertical 9:16 frame.', '16:9': 'Wide 16:9 landscape frame.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('prompt'); ap.add_argument('out'); ap.add_argument('--ref'); ap.add_argument('--aspect', default='4:5', choices=ASPECT)
    ap.add_argument('--raw', action='store_true', help='не добавлять фирменный стиль к промпту')
    a = ap.parse_args()
    key = os.environ.get('IMG_API_KEY', '')
    parts = [{'text': a.prompt + ('' if a.raw else STYLE) + ' ' + ASPECT[a.aspect]}]
    if a.ref:
        parts.append({'inlineData': {'mimeType': 'image/jpeg', 'data': base64.b64encode(Path(a.ref).read_bytes()).decode()}})
    body = json.dumps({'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': {'responseModalities': ['IMAGE']}}).encode()
    err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL + (f'?key={key}' if key else ''), data=body, headers={'Content-Type': 'application/json'})
            d = json.load(urllib.request.urlopen(req, timeout=400))
            for p in d['candidates'][0]['content']['parts']:
                data = p.get('inlineData', {}).get('data')
                m = re.search(r'data:image/\w+;base64,([A-Za-z0-9+/=]+)', p.get('text', ''))
                data = data or (m and m.group(1))
                if data:
                    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
                    Path(a.out).write_bytes(base64.b64decode(data))
                    print(a.out)
                    return
            err = 'в ответе нет картинки'
        except Exception as e:  # noqa: BLE001
            err = e
        time.sleep(5 + attempt * 10)
    sys.exit(f'Не удалось сгенерировать: {err}')


if __name__ == '__main__':
    main()
