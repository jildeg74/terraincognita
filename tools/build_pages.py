"""Generate one static page per question and language, a list page and an about page per language.
Called by build_site.py. Uses the UI strings of the page template (extracted with Node) and tools/strings.json.
"""
import json, os, re, subprocess, html

BASE = 'https://terraincognita.ca'
LANGS = ['en', 'fr', 'zh', 'es', 'hi', 'ar', 'pt']
LNAME = {'en': 'English', 'zh': '中文', 'es': 'Español', 'hi': 'हिन्दी', 'ar': 'العربية', 'fr': 'Français', 'pt': 'Português'}
DKEYS = ['P', 'V', 'E', 'M', 'I', 'T', 'H']
e = lambda s: html.escape(str(s or ''), quote=True)


def extract_ui(page):
    a = page.index('const LANGS=')
    b = page.index('const EXTRA=')
    js = page[a:b] + '\nprocess.stdout.write(JSON.stringify(UI,(k,v)=>typeof v==="function"?undefined:v));'
    return json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)


def extract_tokens(page):
    m = re.search(r'(:root\{.*?:root\[data-theme="light"\]\{.*?\})', page, re.S)
    return m.group(1)


CSS = '''
body{background:var(--bg);color:var(--fg);font:16px/1.6 var(--f-body);margin:0}
.w{max-width:760px;margin:0 auto;padding-block:28px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
a{color:var(--accent)}
.top{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px 16px;margin-bottom:24px}
.brand{font-family:var(--f-display);font-size:26px;color:var(--fg);text-decoration:none;letter-spacing:.02em}
.langs{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:13px}
.langs a[aria-current]{color:var(--fg);font-weight:600;text-decoration:none}
h1{font-size:clamp(24px,4.4vw,34px);line-height:1.2;margin:8px 0 10px;text-wrap:balance}
h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:28px 0 6px;font-weight:600}
p{margin:0 0 10px;max-width:68ch}
.dom{display:inline-flex;align-items:center;gap:8px;font-size:13px;color:var(--muted)}
.dom i{width:10px;height:10px;border-radius:50%;background:var(--c)}
.near{display:inline-block;font:500 12px var(--f-mono);border:1px solid var(--line);border-radius:999px;padding:2px 10px;color:var(--muted)}
ul{padding-inline-start:20px;margin:0}
li{margin:4px 0}
.ty{font:500 11px var(--f-mono);color:var(--muted);border:1px solid var(--line);border-radius:4px;padding:1px 6px;margin-inline-start:6px;white-space:nowrap}
.ty.s{color:var(--fg);border-color:var(--muted)}
.meta{font:12.5px var(--f-mono);color:var(--muted);margin-top:28px}
.cta{display:inline-block;margin-top:18px;font-weight:600}
.group{margin-top:26px}
.group h2{display:flex;align-items:center;gap:8px}
.group h2 i{width:10px;height:10px;border-radius:50%;background:var(--c)}
.group li small{color:var(--muted)}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);font-size:13px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 18px}
'''


def shell(lang, title, desc, path, body, tokens, alt_path):
    d = ' dir="rtl"' if lang == 'ar' else ''
    alts = ''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE}/{l}/{alt_path}">' for l in LANGS)
    return f'''<!doctype html>
<html lang="{lang}"{d}><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}/{path}">{alts}
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}/{path}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>*,*::before,*::after{{box-sizing:border-box}}{tokens}{CSS}</style>
</head><body><div class="w">{body}</div></body></html>
'''


def top(lang, alt_path):
    links = ''.join(f'<a href="../{l}/{alt_path}" hreflang="{l}" lang="{l}"' + (' aria-current="page"' if l == lang else '') + f'>{LNAME[l]}</a>' for l in LANGS)
    return f'<div class="top"><a class="brand" href="../?lang={lang}">Terra Incognita</a><nav class="langs" aria-label="Language">{links}</nav></div>'


def foot(lang, X):
    return (f'<footer><a href="../?lang={lang}">{e(X["map"])}</a><a href="index.html">{e(X["list"])}</a>'
            f'<a href="about.html">{e(X["about"])}</a><a href="../data.json">data.json · CC BY 4.0</a></footer>')


def build(page, docs, out):
    ui = extract_ui(page)
    tokens = extract_tokens(page)
    S = json.load(open(os.path.join(os.path.dirname(__file__), 'strings.json'), encoding='utf-8'))
    by = {d['id']: d for d in docs}
    urls = []
    for lang in LANGS:
        t, X = ui[lang], S[lang]
        os.makedirs(os.path.join(out, lang), exist_ok=True)
        tx = lambda d: {**d['i18n'].get('en', {}), **d['i18n'].get(lang, {})}
        for d in docs:
            a = tx(d)
            subs = ''.join(f'<li>{e(s.get(lang) or s.get("en"))}</li>' for s in d.get('sub', []))
            rel = ''.join(f'<li><a href="{l}.html">{e(tx(by[l])["t"])}</a></li>' for l in d.get('links', []) if l in by)
            srcs = ''.join(
                f'<li><a href="{e(s["u"])}" rel="noopener">{e(s["t"])}</a><span class="ty{" s" if s["ty"] in ("study", "reference") else ""}">{e(t["ty"].get(s["ty"], s["ty"]))}</span></li>'
                for s in d['src'])
            revs = d.get('rev', [])
            rv = (f'<p>{e(t["revBy"])} ' + ', '.join(e(r["name"]) + (f' ({e(r["affil"])})' if r.get('affil') else '') for r in revs) + '</p>') if revs else f'<p class="meta">{e(t["notRev"])}</p>'
            body = (top(lang, d['id'] + '.html') +
                    f'<div class="dom" style="--c:var(--d-{d["d"]})"><i></i>{e(t["dom"][d["d"]])}</div>'
                    f'<h1>{e(a["t"])}</h1><span class="near">{e(t["near"][d["n"]])}</span>'
                    f'<h2>{e(t["known"])}</h2><p>{e(a["known"])}</p>'
                    f'<h2>{e(t["block"])}</h2><p>{e(a["block"])}</p>'
                    f'<h2>{e(t["leads"])}</h2><p>{e(a["leads"])}</p>' +
                    (f'<h2>{e(t["subq"])}</h2><ul>{subs}</ul>' if subs else '') +
                    (f'<h2>{e(t["rel"])}</h2><ul>{rel}</ul>' if rel else '') +
                    f'<h2>{e(t["src"])}</h2><ul>{srcs}</ul>{rv}'
                    f'<p class="meta">{e(X["checked"])}: {e(d.get("checked", ""))}</p>'
                    f'<a class="cta" href="../?lang={lang}#{d["id"]}">{e(X["map"])} {"←" if lang == "ar" else "→"}</a>' + foot(lang, X))
            open(os.path.join(out, lang, d['id'] + '.html'), 'w', encoding='utf-8').write(
                shell(lang, f'{a["t"]} · Terra Incognita', a['known'], f'{lang}/{d["id"]}.html', body, tokens, d['id'] + '.html'))
            urls.append(f'{lang}/{d["id"]}.html')
        groups = ''
        for k in DKEYS:
            items = sorted((d for d in docs if d['d'] == k), key=lambda d: tx(d)['t'])
            if not items:
                continue
            lis = ''.join(f'<li><a href="{d["id"]}.html">{e(tx(d)["t"])}</a> <small>· {e(t["near"][d["n"]])}</small></li>' for d in items)
            groups += f'<section class="group"><h2 style="--c:var(--d-{k})"><i></i>{e(t["dom"][k])}</h2><ul>{lis}</ul></section>'
        body = top(lang, 'index.html') + f'<h1>{e(X["list"])}</h1><p>{e(X["listIntro"])}</p>{groups}' + foot(lang, X)
        open(os.path.join(out, lang, 'index.html'), 'w', encoding='utf-8').write(
            shell(lang, f'{X["list"]} · Terra Incognita', X['listIntro'], f'{lang}/index.html', body, tokens, 'index.html'))
        secs = ''.join(f'<h2>{e(h)}</h2><p>{e(p)}</p>' for h, p in X['aboutBody']).replace('contact@juvason.com', '<a href="mailto:contact@juvason.com">contact@juvason.com</a>')
        body = top(lang, 'about.html') + f'<h1>{e(X["aboutTitle"])}</h1>{secs}' + foot(lang, X)
        open(os.path.join(out, lang, 'about.html'), 'w', encoding='utf-8').write(
            shell(lang, f'{X["aboutTitle"]}', X['aboutBody'][0][1], f'{lang}/about.html', body, tokens, 'about.html'))
        urls += [f'{lang}/index.html', f'{lang}/about.html']
    return urls, {l: {'list': S[l]['list'], 'about': S[l]['about']} for l in LANGS}
