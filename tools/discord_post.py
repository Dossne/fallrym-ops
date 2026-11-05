"""Post one announce/*.md to Discord through the webhook in $DISCORD_WEBHOOK, as «Клавдий».
Discord takes up to 2000 characters a message, so a longer post goes out in parts split by paragraphs."""
import json, os, sys, time, urllib.request

def parts(text, limit=1900):
    out, cur = [], ''
    for para in text.strip().split('\n\n'):
        if len(cur) + len(para) + 2 > limit and cur:
            out.append(cur); cur = ''
        while len(para) > limit:
            out.append(para[:limit]); para = para[limit:]
        cur = (cur + '\n\n' + para) if cur else para
    if cur: out.append(cur)
    return out

def post(url, content):
    body = json.dumps({'username': 'Клавдий', 'content': content, 'allowed_mentions': {'parse': []}}).encode()
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', 'User-Agent': 'fallrym-ops'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as r: return r.status
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(float(json.loads(e.read() or b'{}').get('retry_after', 2))); continue
            raise
    raise SystemExit('Discord kept rate-limiting')

if __name__ == '__main__':
    url = os.environ.get('DISCORD_WEBHOOK')
    if not url: raise SystemExit('DISCORD_WEBHOOK secret is not set')
    text = open(sys.argv[1], encoding='utf-8').read()
    for p in parts(text):
        print(sys.argv[1], 'status', post(url, p)); time.sleep(1)
