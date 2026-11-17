#!/usr/bin/env python3
"""
Мини-клиент VK API для SMM-агента (только стандартная библиотека Python 3.9+).

Токены (.env рядом с папкой scripts или переменные окружения):
  VK_USER_TOKEN   — ключ администратора группы (права: wall, photos, groups, stats, offline).
                    Нужен для публикации постов, загрузки фото, отложки, статистики, поиска групп.
  VK_GROUP_TOKEN  — ключ сообщества (права: messages, manage, photos, wall).
                    Нужен для сообщений сообщества и ответов на комментарии от имени группы.
  VK_GROUP_ID     — числовой ID группы без минуса.

Примеры:
  python3 scripts/vk.py call groups.getById group_id=1
  python3 scripts/vk.py post --text-file data/drafts/2026-11-20.md --photos a.png b.png --at "2026-11-20 13:00"
  python3 scripts/vk.py postponed
  python3 scripts/vk.py unanswered
  python3 scripts/vk.py history 123456
  python3 scripts/vk.py send 123456 --text "Добрый день! ..."
  python3 scripts/vk.py comments --days 3
  python3 scripts/vk.py reply-comment --post 15 --comment 42 --text "Спасибо!"
  python3 scripts/vk.py stats --days 7
"""
import argparse, datetime as dt, json, mimetypes, os, random, sys, time, urllib.parse, urllib.request, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = 'https://api.vk.com/method/'
V = '5.199'
MSK = dt.timezone(dt.timedelta(hours=3))


def load_env():
    f = ROOT / '.env'
    if f.exists():
        for line in f.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()
GID = os.environ.get('VK_GROUP_ID', '').lstrip('-')
_last = [0.0]


def token(kind):
    t = os.environ.get('VK_USER_TOKEN' if kind == 'user' else 'VK_GROUP_TOKEN', '')
    if not t:
        sys.exit(f'Нет {"VK_USER_TOKEN" if kind == "user" else "VK_GROUP_TOKEN"} в .env — см. README.md')
    return t


def call(method, kind='user', **params):
    """Вызов метода API с ограничением ~3 запроса/с и повтором при flood/too many requests."""
    params = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in params.items() if v is not None}
    params.update(access_token=token(kind), v=V)
    for attempt in range(5):
        wait = 0.36 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(API + method, data=urllib.parse.urlencode(params).encode())
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
        if 'error' in d:
            code = d['error'].get('error_code')
            if code in (6, 9, 10) and attempt < 4:  # too many requests / flood / internal
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"VK {method}: [{code}] {d['error'].get('error_msg')}")
        return d['response']


def multipart(url, field, path):
    b = uuid.uuid4().hex
    data = Path(path).read_bytes()
    ctype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    body = (f'--{b}\r\nContent-Disposition: form-data; name="{field}"; filename="{Path(path).name}"\r\n'
            f'Content-Type: {ctype}\r\n\r\n').encode() + data + f'\r\n--{b}--\r\n'.encode()
    req = urllib.request.Request(url, data=body, headers={'Content-Type': f'multipart/form-data; boundary={b}'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def upload_wall_photos(paths):
    """Загружает картинки на стену группы, возвращает список 'photo<owner>_<id>' в исходном порядке."""
    out = []
    for p in paths:
        srv = call('photos.getWallUploadServer', group_id=GID)
        up = multipart(srv['upload_url'], 'photo', p)
        saved = call('photos.saveWallPhoto', group_id=GID, photo=up['photo'], server=up['server'], hash=up['hash'])[0]
        out.append(f"photo{saved['owner_id']}_{saved['id']}")
    return out


def parse_at(s):
    t = dt.datetime.strptime(s, '%Y-%m-%d %H:%M').replace(tzinfo=MSK)
    if t < dt.datetime.now(MSK) + dt.timedelta(minutes=5):
        sys.exit('Время публикации должно быть минимум на 5 минут позже текущего (МСК).')
    return int(t.timestamp())


def log(file, rec):
    f = ROOT / 'data' / file
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + '\n')


def cmd_post(a):
    if os.environ.get('AUTOPUBLISH', '0') != '1' and not a.force:
        sys.exit('AUTOPUBLISH=0: публикация запрещена. Положите черновик в data/drafts/ и дождитесь подтверждения владельца (или --force по прямому указанию владельца).')
    text = Path(a.text_file).read_text(encoding='utf-8').strip() if a.text_file else (a.text or '')
    if text.startswith('---'):  # срезаем YAML-шапку черновика
        text = text.split('---', 2)[2].strip()
    att = upload_wall_photos(a.photos) if a.photos else []
    if a.attach:
        att += a.attach
    params = dict(owner_id=f'-{GID}', from_group=1, message=text, attachments=','.join(att) or None,
                  publish_date=parse_at(a.at) if a.at else None, signed=0)
    if a.poll:
        att.append(a.poll)
        params['attachments'] = ','.join(att)
    r = call('wall.post', **params)
    rec = dict(post_id=r['post_id'], url=f'https://vk.com/wall-{GID}_{r["post_id"]}', at=a.at or dt.datetime.now(MSK).strftime('%Y-%m-%d %H:%M'),
               rubric=a.rubric, format=a.format or ('carousel' if len(a.photos or []) > 1 else 'photo' if a.photos else 'text'),
               topic=a.topic, hook=text.split('\n', 1)[0][:140], postponed=bool(a.at))
    log('posts.jsonl', rec)
    print(json.dumps(rec, ensure_ascii=False, indent=1))


def cmd_poll(a):
    r = call('polls.create', owner_id=f'-{GID}', question=a.question, add_answers=a.answers, is_anonymous=1)
    print(f"poll{r['owner_id']}_{r['id']}")


def cmd_postponed(a):
    r = call('wall.get', owner_id=f'-{GID}', filter='postponed', count=100)
    for p in r['items']:
        t = dt.datetime.fromtimestamp(p['date'], MSK).strftime('%a %d.%m %H:%M')
        print(f"{p['id']:>6}  {t}  {p.get('text', '').splitlines()[0][:90] if p.get('text') else '(без текста)'}")
    print(f"Итого в отложке: {r['count']}")


def cmd_unanswered(a):
    r = call('messages.getConversations', kind='group', group_id=GID, filter='unanswered', count=50, extended=1)
    names = {p['id']: f"{p.get('first_name', '')} {p.get('last_name', '')}".strip() for p in r.get('profiles', [])}
    out = []
    for it in r['items']:
        c, m = it['conversation'], it['last_message']
        pid = c['peer']['id']
        out.append(dict(peer_id=pid, name=names.get(pid, ''), unread=c.get('unread_count', 0),
                        date=dt.datetime.fromtimestamp(m['date'], MSK).strftime('%d.%m %H:%M'), text=m.get('text', ''),
                        attachments=[x['type'] for x in m.get('attachments', [])]))
    print(json.dumps(out, ensure_ascii=False, indent=1))


def cmd_history(a):
    r = call('messages.getHistory', kind='group', group_id=GID, peer_id=a.peer, count=a.count)
    for m in reversed(r['items']):
        who = 'МЫ ' if m.get('out') else 'КЛ '
        t = dt.datetime.fromtimestamp(m['date'], MSK).strftime('%d.%m %H:%M')
        att = ' '.join(f'[{x["type"]}]' for x in m.get('attachments', []))
        print(f'{t} {who}: {m.get("text", "")} {att}')


def cmd_send(a):
    if os.environ.get('AUTOREPLY', '0') != '1' and not a.force:
        sys.exit('AUTOREPLY=0: отправка запрещена. Сохраните черновик ответа в data/drafts/replies.md.')
    text = Path(a.text_file).read_text(encoding='utf-8') if a.text_file else a.text
    r = call('messages.send', kind='group', group_id=GID, peer_id=a.peer, message=text, random_id=random.randint(1, 2**31))
    call('messages.markAsRead', kind='group', group_id=GID, peer_id=a.peer)
    log('replies.jsonl', dict(peer_id=a.peer, at=dt.datetime.now(MSK).isoformat(timespec='minutes'), text=text, msg_id=r))
    print('отправлено', r)


def cmd_comments(a):
    since = time.time() - a.days * 86400
    posts = call('wall.get', owner_id=f'-{GID}', count=30)['items']
    out = []
    for p in posts:
        if p['date'] < since or not p.get('comments', {}).get('count'):
            continue
        cm = call('wall.getComments', owner_id=f'-{GID}', post_id=p['id'], count=100, sort='asc', thread_items_count=10, extended=1)
        names = {u['id']: f"{u.get('first_name', '')} {u.get('last_name', '')}".strip() for u in cm.get('profiles', [])}
        for c in cm['items']:
            if c.get('from_id') == -int(GID) or c.get('deleted'):
                continue
            thread = c.get('thread', {}).get('items', [])
            answered = any(t.get('from_id') == -int(GID) for t in thread)
            if not answered:
                out.append(dict(post=p['id'], comment=c['id'], from_id=c['from_id'], name=names.get(c['from_id'], ''),
                                text=c.get('text', ''), url=f'https://vk.com/wall-{GID}_{p["id"]}?reply={c["id"]}'))
    print(json.dumps(out, ensure_ascii=False, indent=1))


def cmd_reply_comment(a):
    if os.environ.get('AUTOREPLY', '0') != '1' and not a.force:
        sys.exit('AUTOREPLY=0: ответ запрещён. Сохраните черновик в data/drafts/replies.md.')
    r = call('wall.createComment', owner_id=f'-{GID}', post_id=a.post, reply_to_comment=a.comment, from_group=GID, message=a.text)
    log('replies.jsonl', dict(post=a.post, comment=a.comment, at=dt.datetime.now(MSK).isoformat(timespec='minutes'), text=a.text))
    print('ответ', r.get('comment_id'))


def cmd_stats(a):
    now = int(time.time())
    st = call('stats.get', group_id=GID, timestamp_from=now - a.days * 86400, timestamp_to=now, interval='day', extended=1)
    posts = call('wall.get', owner_id=f'-{GID}', count=100)['items']
    since = now - a.days * 86400
    rows = []
    for p in posts:
        if p['date'] < since:
            continue
        views = p.get('views', {}).get('count', 0)
        l, c, r = p['likes']['count'], p['comments']['count'], p['reposts']['count']
        rows.append(dict(id=p['id'], date=dt.datetime.fromtimestamp(p['date'], MSK).strftime('%a %d.%m %H:%M'), views=views,
                         likes=l, comments=c, reposts=r, erv=round(100 * (l + c + r) / views, 2) if views else None,
                         hook=(p.get('text') or '').split('\n', 1)[0][:80]))
    print(json.dumps(dict(stats=st, posts=rows), ensure_ascii=False, indent=1))


def cmd_call(a):
    params = dict(kv.split('=', 1) for kv in a.params)
    print(json.dumps(call(a.method, kind=a.kind, **params), ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('call'); p.add_argument('method'); p.add_argument('params', nargs='*'); p.add_argument('--kind', default='user', choices=['user', 'group']); p.set_defaults(f=cmd_call)
    p = sp.add_parser('post', help='опубликовать или поставить в отложку')
    p.add_argument('--text-file'); p.add_argument('--text'); p.add_argument('--photos', nargs='*'); p.add_argument('--attach', nargs='*', help='готовые вложения: video-1_2, poll-1_3, https://...')
    p.add_argument('--poll', help='вложение опроса из команды poll'); p.add_argument('--at', help='"ГГГГ-ММ-ДД ЧЧ:ММ" по МСК — в отложку')
    p.add_argument('--rubric'); p.add_argument('--format'); p.add_argument('--topic'); p.add_argument('--force', action='store_true'); p.set_defaults(f=cmd_post)
    p = sp.add_parser('poll'); p.add_argument('--question', required=True); p.add_argument('--answers', nargs='+', required=True); p.set_defaults(f=cmd_poll)
    p = sp.add_parser('postponed'); p.set_defaults(f=cmd_postponed)
    p = sp.add_parser('unanswered'); p.set_defaults(f=cmd_unanswered)
    p = sp.add_parser('history'); p.add_argument('peer', type=int); p.add_argument('--count', type=int, default=30); p.set_defaults(f=cmd_history)
    p = sp.add_parser('send'); p.add_argument('peer', type=int); p.add_argument('--text'); p.add_argument('--text-file'); p.add_argument('--force', action='store_true'); p.set_defaults(f=cmd_send)
    p = sp.add_parser('comments'); p.add_argument('--days', type=int, default=3); p.set_defaults(f=cmd_comments)
    p = sp.add_parser('reply-comment'); p.add_argument('--post', type=int, required=True); p.add_argument('--comment', type=int, required=True); p.add_argument('--text', required=True); p.add_argument('--force', action='store_true'); p.set_defaults(f=cmd_reply_comment)
    p = sp.add_parser('stats'); p.add_argument('--days', type=int, default=7); p.set_defaults(f=cmd_stats)
    a = ap.parse_args()
    a.f(a)


if __name__ == '__main__':
    main()
