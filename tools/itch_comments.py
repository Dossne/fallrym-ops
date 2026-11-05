"""Collect the comments from an itch.io game page into comments/itch.json (all of them) and comments/new.md (what
appeared since the last run, newest first). The page is plain HTML: every comment is a div.community_post with
an author, a date (title attribute) and a body. Older comments are behind «?before=» links — followed up to 10 pages."""
import html, json, os, re, sys, urllib.error, urllib.request
from html.parser import HTMLParser

UA = {'User-Agent': 'fallrym-ops comments (github actions)'}

class Posts(HTMLParser):
    def __init__(self):
        super().__init__(); self.posts = []; self.cur = None; self.depth = 0; self.field = None; self.fdepth = 0
    def handle_starttag(self, tag, a):
        a = dict(a); cls = a.get('class') or ''
        if tag == 'div' and 'community_post' in cls.split() and (a.get('id') or '').startswith('post-'):
            self.cur = {'id': a['id'][5:], 'author': '', 'date': '', 'text': ''}; self.depth = 1; return
        if not self.cur: return
        if tag == 'div': self.depth += 1
        if 'post_author' in cls: self.field, self.fdepth = 'author', self.depth
        elif 'post_date' in cls: self.cur['date'] = a.get('title') or ''
        elif 'post_body' in cls: self.field, self.fdepth = 'text', self.depth
        elif tag in ('br', 'p') and self.field == 'text': self.cur['text'] += '\n'
    def handle_endtag(self, tag):
        if not self.cur: return
        if tag == 'div':
            if self.field == 'text' and self.depth == self.fdepth: self.field = None
            self.depth -= 1
            if self.depth == 0:
                self.cur = {k: v.strip() for k, v in self.cur.items()}; self.posts.append(self.cur); self.cur = None; self.field = None
        if tag in ('span', 'a') and self.field == 'author': self.field = None
    def handle_data(self, d):
        if self.cur and self.field: self.cur[self.field] += d

def get(url):
    import time
    for wait in (0, 30, 90, 180):  # itch answers 429 now and then to shared runners: wait and try again
        time.sleep(wait)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            print(f'{url}: 429, retrying')
    raise SystemExit('itch kept answering 429')

def collect(url):
    seen, posts, page = set(), [], url
    for _ in range(10):
        h = get(page); p = Posts(); p.feed(h)
        print(f'{page}: {len(h)} bytes, community_post×{h.count("community_post")}, comment×{h.lower().count("comment")}, parsed {len(p.posts)}')
        if not p.posts and os.environ.get('ITCH_DEBUG'):
            for m in list(re.finditer(r'community_post', h))[:4]: print('…', h[max(0, m.start() - 200):m.start() + 400].replace('\n', ' '))
        for x in p.posts:
            if x['id'] not in seen: seen.add(x['id']); posts.append(x)
        m = re.search(r'href="([^"]+\?before=\d+[^"]*)"', h)
        if not m: break
        page = html.unescape(m.group(1)); page = page if page.startswith('http') else 'https://itch.io' + page
    return posts

if __name__ == '__main__':
    url = sys.argv[1]; os.makedirs('comments', exist_ok=True)
    old = []
    if os.path.exists('comments/itch.json'):
        old = json.load(open('comments/itch.json', encoding='utf-8'))
    have = {x['id'] for x in old}
    posts = collect(url)
    new = [x for x in posts if x['id'] not in have]
    allp = {x['id']: x for x in old}; allp.update({x['id']: x for x in posts})
    json.dump(sorted(allp.values(), key=lambda x: x['date'], reverse=True), open('comments/itch.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lines = [f'# Новые комментарии на itch ({len(new)})', '', f'Страница: {url}', '']
    for x in sorted(new, key=lambda x: x['date'], reverse=True):
        lines += [f"**{x['author']}** · {x['date']}", '', x['text'], '', '---', '']
    if not new: lines.append('Новых нет.')
    open('comments/new.md', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(f'{len(posts)} on the page, {len(new)} new')
