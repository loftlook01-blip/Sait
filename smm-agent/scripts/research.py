#!/usr/bin/env python3
"""
Анализ конкурентов и собственной группы во ВКонтакте.

  # 1. Найти кандидатов по ключевым запросам (сортировка по числу участников)
  python3 scripts/research.py find "мебель из массива" "лофт мебель на заказ" "стол из слэба" "мебель из металла и дерева"

  # 2. Выгрузить последние посты групп (screen_name или id), по 100 на группу
  python3 scripts/research.py collect woodgroup1 loft_mebel 12345 --count 100

  # 3. Отчёт: форматы, время, длина текста, топ-посты по «перевыполнению» медианы группы
  python3 scripts/research.py report data/research/posts-2026-11-17.csv

Ключевая метрика — lift: (лайки+комментарии+репосты) поста / медиана того же показателя по группе.
Это честно сравнивает посты маленьких и больших групп. ERV = реакции / просмотры × 100%.
"""
import argparse, csv, datetime as dt, json, statistics as st, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from vk import call, MSK, ROOT  # noqa: E402

OUT = ROOT / 'data' / 'research'
WD = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


def cmd_find(a):
    seen = {}
    for q in a.queries:
        r = call('groups.search', q=q, count=a.count, sort=0, **({'city_id': a.city} if a.city else {}))
        ids = ','.join(str(g['id']) for g in r['items'])
        if not ids:
            continue
        info = call('groups.getById', group_ids=ids, fields='members_count,activity,description,site,city,status,verified')
        info = info['groups'] if isinstance(info, dict) else info
        for g in info:
            if g.get('is_closed') or g.get('deactivated'):
                continue
            seen[g['id']] = dict(id=g['id'], screen_name=g.get('screen_name'), name=g['name'], members=g.get('members_count', 0),
                                 activity=g.get('activity', ''), city=(g.get('city') or {}).get('title', ''), query=q,
                                 url=f"https://vk.com/{g.get('screen_name') or 'club' + str(g['id'])}")
    rows = sorted(seen.values(), key=lambda x: -x['members'])
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f'candidates-{dt.date.today()}.csv'
    with f.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ['id'])
        w.writeheader(); w.writerows(rows)
    for r in rows[:40]:
        print(f"{r['members']:>8}  {r['url']:<40} {r['name'][:50]}  [{r['city']}]")
    print(f'\nСохранено: {f}')


def fmt_of(p):
    att = [x['type'] for x in p.get('attachments', [])]
    if any(x == 'video' for x in att):
        v = next(x['video'] for x in p['attachments'] if x['type'] == 'video')
        return 'clip' if v.get('type') == 'short_video' or (v.get('height', 0) > v.get('width', 1)) else 'video'
    if 'poll' in att:
        return 'poll'
    n = att.count('photo')
    if n >= 3:
        return 'carousel'
    if n:
        return 'photo'
    if 'link' in att or 'article' in att:
        return 'link'
    return 'text'


def cmd_collect(a):
    rows = []
    for g in a.groups:
        info = call('groups.getById', group_id=g, fields='members_count')
        info = (info['groups'] if isinstance(info, dict) else info)[0]
        members = info.get('members_count', 0)
        got, offset = [], 0
        while len(got) < a.count:
            r = call('wall.get', owner_id=-info['id'], count=min(100, a.count - len(got)), offset=offset)
            if not r['items']:
                break
            got += r['items']; offset += len(r['items'])
        for p in got:
            if p.get('is_pinned') or p.get('marked_as_ads'):
                continue
            t = dt.datetime.fromtimestamp(p['date'], MSK)
            l, c, rp = p['likes']['count'], p['comments']['count'], p['reposts']['count']
            views = (p.get('views') or {}).get('count') or 0
            text = (p.get('text') or '').replace('\r', '')
            rows.append(dict(group=info.get('screen_name') or info['id'], members=members, post_id=p['id'],
                             url=f"https://vk.com/wall-{info['id']}_{p['id']}", date=t.strftime('%Y-%m-%d'), weekday=WD[t.weekday()],
                             hour=t.hour, format=fmt_of(p), photos=sum(1 for x in p.get('attachments', []) if x['type'] == 'photo'),
                             text_len=len(text), likes=l, comments=c, reposts=rp, views=views, reactions=l + c + rp,
                             erv=round(100 * (l + c + rp) / views, 2) if views else '', hook=text.split('\n', 1)[0][:160],
                             text=text[:1200]))
        print(f'{g}: {len(got)} постов, {members} участников', file=sys.stderr)
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f'posts-{dt.date.today()}.csv'
    with f.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f)


def med(xs):
    xs = [x for x in xs if x != '' and x is not None]
    return round(st.median(xs), 2) if xs else 0


def cmd_report(a):
    rows = list(csv.DictReader(open(a.csv, encoding='utf-8')))
    for r in rows:
        for k in ('reactions', 'comments', 'views', 'hour', 'text_len', 'members', 'reposts'):
            r[k] = int(r[k] or 0)
        r['erv'] = float(r['erv']) if r['erv'] else None
    by_g = defaultdict(list)
    for r in rows:
        by_g[r['group']].append(r)
    for g, ps in by_g.items():
        m = med([p['reactions'] for p in ps]) or 1
        for p in ps:
            p['lift'] = round(p['reactions'] / m, 2)
    L = [f'# Отчёт по конкурентам ({a.csv})', '', '## Группы', '', '| Группа | Участники | Постов | Медиана реакций | Медиана просмотров | Медиана ERV % | Постов в неделю |', '|---|---|---|---|---|---|---|']
    for g, ps in sorted(by_g.items(), key=lambda x: -x[1][0]['members']):
        ds = sorted(p['date'] for p in ps)
        weeks = max(1, (dt.date.fromisoformat(ds[-1]) - dt.date.fromisoformat(ds[0])).days / 7)
        L.append(f"| {g} | {ps[0]['members']} | {len(ps)} | {med([p['reactions'] for p in ps])} | {med([p['views'] for p in ps])} | {med([p['erv'] for p in ps])} | {round(len(ps) / weeks, 1)} |")

    def table(title, key, order=None):
        agg = defaultdict(list)
        for r in rows:
            agg[key(r)].append(r)
        keys = order or sorted(agg, key=lambda k: -med([p['lift'] for p in agg[k]]))
        L.extend(['', f'## {title}', '', '| Значение | Постов | Медиана lift | Медиана ERV % | Медиана комментариев |', '|---|---|---|---|---|'])
        for k in keys:
            if k in agg:
                ps = agg[k]
                L.append(f"| {k} | {len(ps)} | {med([p['lift'] for p in ps])} | {med([p['erv'] for p in ps])} | {med([p['comments'] for p in ps])} |")

    table('Формат', lambda r: r['format'])
    table('День недели', lambda r: r['weekday'], WD)
    table('Час публикации (МСК)', lambda r: f"{r['hour']:02d}:00", [f'{h:02d}:00' for h in range(24)])
    table('Длина текста', lambda r: '0–200' if r['text_len'] < 200 else '200–600' if r['text_len'] < 600 else '600–1200' if r['text_len'] < 1200 else '1200+',
          ['0–200', '200–600', '600–1200', '1200+'])
    top = sorted(rows, key=lambda r: -r['lift'])[:a.top]
    L.extend(['', f'## Топ-{a.top} постов по lift (во сколько раз пост лучше типичного поста своей группы)', ''])
    for r in top:
        L.append(f"- **×{r['lift']}** · {r['format']} · {r['reactions']} реакц. / {r['comments']} комм. / {r['views']} просм. · {r['weekday']} {r['hour']}:00 · [{r['group']}]({r['url']})\n  > {r['hook']}")
    talk = sorted(rows, key=lambda r: -r['comments'])[:15]
    L.extend(['', '## Самые обсуждаемые (комментарии)', ''])
    for r in talk:
        L.append(f"- {r['comments']} комм. · {r['format']} · [{r['group']}]({r['url']}) — {r['hook']}")
    L.extend(['', '## Что сделать агенту дальше', '',
              '1. Прочитать тексты топ-постов (колонка text в CSV) и присвоить каждому тему и рубрику из strategy/rubricator.md.',
              '2. Найти 5–7 повторяющихся паттернов (тема × формат × крючок) и записать в data/insights.md с примерами-ссылками.',
              '3. Добавить 10+ новых идей в data/ideas.md, адаптированных под наш цех и Архангельск (не копировать!).'])
    f = Path(a.csv).with_suffix('.report.md')
    f.write_text('\n'.join(L), encoding='utf-8')
    print(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('find'); p.add_argument('queries', nargs='+'); p.add_argument('--count', type=int, default=50); p.add_argument('--city', type=int, help='city_id VK; узнать: vk.py call database.getCities country_id=1 q=Архангельск'); p.set_defaults(f=cmd_find)
    p = sp.add_parser('collect'); p.add_argument('groups', nargs='+'); p.add_argument('--count', type=int, default=100); p.set_defaults(f=cmd_collect)
    p = sp.add_parser('report'); p.add_argument('csv'); p.add_argument('--top', type=int, default=25); p.set_defaults(f=cmd_report)
    a = ap.parse_args(); a.f(a)


if __name__ == '__main__':
    main()
