"""Build the public static site of Terra Incognita.
Usage: python3 build_site.py PAGE_HTML QUESTIONS_DIR CHANGES_DIR OUT_DIR [DIGESTS_DIR]
QUESTIONS_DIR / CHANGES_DIR: one JSON file per document (as saved by ArtifactData list with out_dir).
"""
import json, glob, os, sys
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
<meta property="og:image" content="https://terraincognita.ca/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://terraincognita.ca/">
<style>*,*::before,*::after{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style>
'''
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
        x = {k: v for k, v in d.items() if k not in ('i18n', 'sub')}
        x['i18n'] = {l: d['i18n'][l]}
        if d.get('sub'):
            x['sub'] = [{l: q[l]} for q in d['sub']]
        part.append(x)
    open(os.path.join(out, 'q', l + '.json'), 'w').write(json.dumps(part, ensure_ascii=False, separators=(',', ':')))
import shutil
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'og.png'), os.path.join(out, 'og.png'))
updated = max([d.get('checked', '') for d in docs] + [c.get('date', '') for c in changes])
open(os.path.join(out, 'data.json'), 'w').write(json.dumps({
    'name': 'Terra Incognita', 'license': 'CC BY 4.0', 'url': 'https://terraincognita.ca/',
    'updated': updated, 'questions': docs, 'changes': changes, 'digests': digests}, ensure_ascii=False, indent=1))
open(os.path.join(out, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\nSitemap: https://terraincognita.ca/sitemap.xml\n')
locs = [''] + urls
open(os.path.join(out, 'sitemap.xml'), 'w').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'<url><loc>https://terraincognita.ca/{u}</loc><lastmod>{updated}</lastmod></url>\n' for u in locs) + '</urlset>\n')
print(f'built {len(docs)} questions, {len(urls)} pages, {len(changes)} change entries, updated {updated}')
