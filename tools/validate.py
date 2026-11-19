"""Validate the Terra Incognita dataset. Exit code 1 on any error.

Usage: python3 tools/validate.py [DATA_DIR]   (default: data)
Errors block publication; warnings are printed but allowed.
"""
import json, os, re, sys, glob

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data'
LANGS = ['en', 'fr', 'zh', 'es', 'hi', 'ar', 'pt']
DOMAINS = set('PVEMITH')
FIELDS = ['t', 's', 'known', 'block', 'leads']
TYPES = {'study', 'preprint', 'official', 'institution', 'reference', 'press', 'company', 'encyclopedia'}
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
ID = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

errors, warnings = [], []
def err(m): errors.append(m)
def warn(m): warnings.append(m)

qs = {}
for f in sorted(glob.glob(os.path.join(DATA, 'questions', '*.json'))):
    i = os.path.basename(f)[:-5]
    try:
        qs[i] = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        err(f'{i}: invalid JSON ({e})')
if len(qs) < 100:
    err(f'only {len(qs)} questions found; the map must never shrink below 100')

for i, q in qs.items():
    if not ID.match(i): err(f'{i}: id must be lowercase words joined by hyphens')
    if q.get('d') not in DOMAINS: err(f'{i}: d must be one of {sorted(DOMAINS)}')
    if q.get('n') not in (0, 1, 2, 3): err(f'{i}: n must be 0, 1, 2 or 3 (3 = solved)')
    if q.get('n') == 3 and not DATE.match(str(q.get('solved', '')) ): err(f'{i}: a solved question (n=3) needs "solved": "YYYY-MM-DD"')
    for l in q.get('links', []):
        if l not in qs: err(f'{i}: link to unknown question {l}')
    i18n = q.get('i18n', {})
    for lang in LANGS:
        for k in FIELDS:
            if not str(i18n.get(lang, {}).get(k, '')).strip():
                err(f'{i}: missing {lang}.{k}')
    whys = [lang for lang in LANGS if str(i18n.get(lang, {}).get('why', '')).strip()]
    if whys and len(whys) < len(LANGS): err(f'{i}: "why" must be in all 7 languages or none (has {whys})')
    if not whys: warn(f'{i}: no "why it matters" yet')
    src = q.get('src', [])
    if not 1 <= len(src) <= 3: err(f'{i}: needs 1 to 3 sources (has {len(src)})')
    for s in src:
        if not str(s.get('u', '')).startswith('https://'): err(f'{i}: source url must be https: {s.get("u")}')
        if not str(s.get('t', '')).strip(): err(f'{i}: source without title')
        if s.get('ty') not in TYPES: err(f'{i}: source type must be one of {sorted(TYPES)}')
    if src and not any(s.get('ty') in ('study', 'reference') for s in src):
        warn(f'{i}: no peer-reviewed study or academic reference yet')
    if src and all(s.get('ty') in ('press', 'company', 'encyclopedia') for s in src):
        err(f'{i}: sources are only press/company/encyclopedia')
    dsrc = q.get('dsrc', [])
    dets = [lang for lang in LANGS if i18n.get(lang, {}).get('detail')]
    if dets or dsrc:
        if len(dets) < len(LANGS): err(f'{i}: "detail" must be in all 7 languages (has {dets})')
        if not 1 <= len(dsrc) <= 12: err(f'{i}: "detail" needs 1 to 12 sources in "dsrc" (has {len(dsrc)})')
        for s in dsrc:
            if not str(s.get('u', '')).startswith('https://'): err(f'{i}: dsrc url must be https: {s.get("u")}')
            if not str(s.get('t', '')).strip() or s.get('ty') not in TYPES: err(f'{i}: dsrc entry needs a title and a valid type')
        en = i18n.get('en', {}).get('detail', {}) or {}
        used = set()
        for k in ('state', 'ideas', 'settle', 'recent'):
            ref = re.findall(r'\[(\d+)\]', str(en.get(k, '')))
            if not str(en.get(k, '')).strip(): err(f'{i}: detail.{k} missing in en')
            # every English sentence must carry at least one citation
            for sent in re.split(r'(?<=[.!?])(?<!\s[A-Z]\.)\s+(?=[A-Z])', str(en.get(k, '')).strip()):
                if sent and not re.search(r'\[\d+\]', sent): err(f'{i}: detail.{k} (en) sentence without a citation: {sent[:60]}')
            for r in ref:
                used.add(int(r))
                if not 1 <= int(r) <= len(dsrc): err(f'{i}: detail.{k} cites [{r}] but dsrc has {len(dsrc)} entries')
            for lang in LANGS:
                other = re.findall(r'\[(\d+)\]', str((i18n.get(lang, {}).get('detail') or {}).get(k, '')))
                if sorted(other) != sorted(ref): err(f'{i}: detail.{k} in {lang} does not cite the same sources as English ({other} vs {ref})')
        for n in range(1, len(dsrc) + 1):
            if n not in used: warn(f'{i}: dsrc [{n}] is never cited')
    for n, sq in enumerate(q.get('sub', [])):
        for lang in LANGS:
            if not str(sq.get(lang, '')).strip(): err(f'{i}: sub-question {n} missing {lang}')
    for r in q.get('rev', []):
        if not str(r.get('name', '')).strip(): err(f'{i}: reviewer without name')
    if 'checked' in q and not DATE.match(str(q['checked'])): err(f'{i}: checked must be YYYY-MM-DD')

for f in glob.glob(os.path.join(DATA, 'changes', '*.json')):
    c = json.load(open(f, encoding='utf-8'))
    if not DATE.match(str(c.get('date', ''))): err(f'{f}: bad date')
    for it in c.get('items', []):
        if 'q' in it and it['q'] not in qs: err(f'{f}: change refers to unknown question {it["q"]}')

for f in glob.glob(os.path.join(DATA, 'digests', '*.json')):
    d = json.load(open(f, encoding='utf-8'))
    if not re.match(r'^\d{4}-\d{2}$', str(d.get('month', ''))): err(f'{f}: bad month')
    for lang in LANGS:
        if not str(d.get('i18n', {}).get(lang, {}).get('body', '')).strip(): err(f'{f}: missing {lang} body')

for w in warnings: print('warning:', w)
for e in errors: print('ERROR:', e)
strong = sum(1 for q in qs.values() if any(s.get('ty') in ('study', 'reference') for s in q.get('src', [])))
print(f'{len(qs)} questions, {strong} with a peer-reviewed study or academic reference, '
      f'{sum(len(q.get("sub", [])) for q in qs.values())} sub-questions, {len(errors)} errors, {len(warnings)} warnings')
sys.exit(1 if errors else 0)
