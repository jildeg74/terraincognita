"""Build the public static site of Terra Incognita.
Usage: python3 build_site.py PAGE_HTML QUESTIONS_DIR CHANGES_DIR OUT_DIR [DIGESTS_DIR]
QUESTIONS_DIR / CHANGES_DIR: one JSON file per document (as saved by ArtifactData list with out_dir).
"""
import re, json, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pages

page_path, qdir, cdir, out = sys.argv[1:5]
ddir = sys.argv[5] if len(sys.argv) > 5 else None
docs = []
for f in sorted(glob.glob(os.path.join(qdir, '*.json'))):
    docs.append({'id': os.path.basename(f)[:-5], **json.load(open(f))})
changes = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(cdir, '*.json')))]
digests = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ddir, '*.json')))] if ddir else []
assert len(docs) >= 100, 'expected at least 100 questions'

page = open(page_path).read()
src_page = page
start = page.index('(async()=>{')
end = page.index('})();', start) + len('})();')
dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
inline = ('const CHANGES=' + dump(changes) + ';\nconst DIGESTS=' + dump(digests) + ';\n'
          'changes=CHANGES;digests=DIGESTS;renderDigest();\n'
          'const TI_DONE=new Set();\n'
          'window.TI_LOAD=async function(l){if(TI_DONE.has(l))return;const r=await fetch("q/"+l+".json");if(!r.ok)throw new Error("load");const d=await r.json();TI_DONE.add(l);'
          'if(!nodes.length){ingest(d.map(x=>{const {id,...rest}=x;return {id,data:()=>rest}}));return}'
          'for(const x of d){const n=byId[x.id];if(!n)continue;n.i18n={...(n.i18n||{}),...(x.i18n||{})};(x.sub||[]).forEach((q,i)=>{if(n.sub&&n.sub[i])Object.assign(n.sub[i],q)})}};\n'
          '(async()=>{const timer=setTimeout(()=>{if(!nodes.length)setStatus("slow")},10000);'
          'try{await TI_LOAD(lang)}catch(e){try{await TI_LOAD("en")}catch(e2){setStatus("err")}}clearTimeout(timer);'
          'if(nodes.length&&!(byId[nodes[0].id].i18n||{})[lang])applyLang()})();')
page = page[:start] + inline + page[end:]
page = page.replace('<meta name="claude:viewport-fit-sides" content="cover">', '')
head = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="A living map of what humanity does not know yet: great open questions, linked and sourced, in seven languages.">
<meta property="og:title" content="Terra Incognita">
<meta property="og:description" content="A living map of what humanity does not know yet.">
<meta property="og:url" content="https://terraincognita.ca/">
<meta property="og:type" content="website"><meta property="og:site_name" content="Terra Incognita">
<meta property="og:image" content="https://terraincognita.ca/og.jpg?v=3"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://terraincognita.ca/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png"><link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png"><link rel="icon" href="/favicon-192.png" sizes="192x192" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>*,*::before,*::after{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style>
'''
LD = {'@context': 'https://schema.org', '@type': 'Dataset', 'name': 'Terra Incognita',
      'description': 'A living map of the great open questions of science: for each question, what we know, what blocks us, current leads, research sub-questions and typed sources, in seven languages, checked every week.',
      'url': 'https://terraincognita.ca/', 'identifier': 'https://doi.org/10.5281/zenodo.24356516',
      'license': 'https://creativecommons.org/licenses/by/4.0/', 'isAccessibleForFree': True,
      'inLanguage': ['en', 'fr', 'zh', 'es', 'hi', 'ar', 'pt'],
      'keywords': ['open questions', 'unsolved problems', 'science', 'research frontier', 'open data'],
      'creator': {'@type': 'Organization', 'name': 'Terra Incognita contributors'},
      'publisher': {'@type': 'Organization', 'name': 'Juvason', 'email': 'contact@terraincognita.ca'},
      'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'application/json', 'contentUrl': 'https://terraincognita.ca/data.json'}]}
head = head.replace('<style>', '<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + '</script>\n<style>', 1)
te = page.index('</title>') + len('</title>')
html = head + page[:te] + '\n' + page[te:].replace('<div class="wrap">', '</head><body>\n<div class="wrap">', 1) + '\n</body></html>\n'

os.makedirs(out, exist_ok=True)
urls, extra = build_pages.build(src_page, docs, out, changes)
html = html.replace('const EXTRA={};', 'const EXTRA=' + dump(extra) + ';', 1)
open(os.path.join(out, 'index.html'), 'w').write(html)
os.makedirs(os.path.join(out, 'q'), exist_ok=True)
for l in build_pages.LANGS:
    part = []
    for d in docs:
        x = {k: v for k, v in d.items() if k not in ('i18n', 'sub', 'dsrc')}
        x['i18n'] = {l: {k: v for k, v in d['i18n'][l].items() if k != 'detail'}}  # 'In depth' text only on question pages
        if d.get('dsrc'):  # flags only: the 'In depth' text stays on the question pages
            x['dn'] = len(d['dsrc'])
            x['dm'] = max(1, round(sum(len(re.sub(r'\[\d+\]', '', v).split()) for v in d['i18n']['en']['detail'].values()) / 200))
        if d.get('sub'):
            x['sub'] = [{l: q[l]} for q in d['sub']]
        part.append(x)
    open(os.path.join(out, 'q', l + '.json'), 'w').write(json.dumps(part, ensure_ascii=False, separators=(',', ':')))
import shutil
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo')
for src, dst in (('logo.svg', 'favicon.svg'), ('favicon-32.png', 'favicon-32.png'), ('apple-touch-icon.png', 'apple-touch-icon.png'), ('logo-512.png', 'logo-512.png'), ('favicon-48.png', 'favicon-48.png'), ('favicon-192.png', 'favicon-192.png'), ('favicon.ico', 'favicon.ico')):
    shutil.copy(os.path.join(L, src), os.path.join(out, dst))
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'og.jpg'), os.path.join(out, 'og.jpg'))
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'header-map.jpg'), os.path.join(out, 'header-map.jpg'))
updated = max([d.get('checked', '') for d in docs] + [c.get('date', '') for c in changes])
open(os.path.join(out, 'data.json'), 'w').write(json.dumps({
    'name': 'Terra Incognita', 'license': 'CC BY 4.0', 'url': 'https://terraincognita.ca/',
    'updated': updated, 'questions': docs, 'changes': changes, 'digests': digests}, ensure_ascii=False, indent=1))
open(os.path.join(out, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\nSitemap: https://terraincognita.ca/sitemap.xml\n')
LD['dateModified'] = updated
html = html.replace('"isAccessibleForFree": true', '"isAccessibleForFree": true, "dateModified": "' + updated + '"', 1)
open(os.path.join(out, 'index.html'), 'w').write(html)
en = sorted(docs, key=lambda d: d['i18n']['en']['t'])
open(os.path.join(out, 'llms.txt'), 'w').write(
    '# Terra Incognita\n\n> A living map of what humanity does not know yet: ' + str(len(docs)) + ' great open scientific questions, linked together. '
    'For each: what we know, what blocks us, current leads, research sub-questions and typed sources (peer-reviewed study, preprint, official, press...). '
    'Seven languages: en, fr, zh, es, hi, ar, pt. Checked every week; nothing is written without a source that was actually read, and changes are re-checked by an independent verifier. '
    'Not yet reviewed by domain specialists. Last update: ' + updated + '.\n\n'
    '## Data\n\n- [Full dataset, all languages (JSON)](https://terraincognita.ca/data.json): questions, sources, sub-questions, change log. License CC BY 4.0.\n'
    + ''.join(f'- [Questions in {l} (JSON)](https://terraincognita.ca/q/{l}.json)\n' for l in build_pages.LANGS) +
    '- Cite as: Terra Incognita contributors, Terra Incognita, DOI https://doi.org/10.5281/zenodo.24356516\n\n'
    '## Pages\n\n- [About and method](https://terraincognita.ca/en/about.html)\n- [All questions by field](https://terraincognita.ca/en/index.html)\n'
    '- Each question has one page per language: https://terraincognita.ca/<lang>/<id>.html\n\n'
    '## Questions (English)\n\n' + ''.join(f"- [{d['i18n']['en']['t']}](https://terraincognita.ca/en/{d['id']}.html)\n" for d in en) +
    '\n## Contact\n\ncontact@terraincognita.ca (publisher: Juvason, Montréal, Canada)\n')
locs = [''] + urls
open(os.path.join(out, 'sitemap.xml'), 'w').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'<url><loc>https://terraincognita.ca/{u}</loc><lastmod>{updated}</lastmod></url>\n' for u in locs) + '</urlset>\n')
print(f'built {len(docs)} questions, {len(urls)} pages, {len(changes)} change entries, updated {updated}')
