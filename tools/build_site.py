"""Build the public static site of Terra Incognita.
Usage: python3 build_site.py PAGE_HTML QUESTIONS_DIR CHANGES_DIR OUT_DIR [DIGESTS_DIR]
QUESTIONS_DIR / CHANGES_DIR: one JSON file per document (as saved by ArtifactData list with out_dir).
"""
import json, glob, os, sys

page_path, qdir, cdir, out = sys.argv[1:5]
ddir = sys.argv[5] if len(sys.argv) > 5 else None
docs = []
for f in sorted(glob.glob(os.path.join(qdir, '*.json'))):
    docs.append({'id': os.path.basename(f)[:-5], **json.load(open(f))})
changes = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(cdir, '*.json')))]
digests = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ddir, '*.json')))] if ddir else []
assert len(docs) >= 100, 'expected at least 100 questions'

page = open(page_path).read()
start = page.index('(async()=>{')
end = page.index('})();', start) + len('})();')
dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
inline = ('const DATA=' + dump(docs) + ';\nconst CHANGES=' + dump(changes) + ';\nconst DIGESTS=' + dump(digests) + ';\n'
          'changes=CHANGES;digests=DIGESTS;renderDigest();\ningest(DATA.map(d=>{const {id,...rest}=d;return {id,data:()=>rest}}));')
page = page[:start] + inline + page[end:]
page = page.replace('<meta name="claude:viewport-fit-sides" content="cover">', '')
head = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="A living map of what humanity does not know yet: great open questions, linked and sourced, in seven languages.">
<meta property="og:title" content="Terra Incognita">
<meta property="og:description" content="A living map of what humanity does not know yet.">
<meta property="og:url" content="https://www.terraincognita.ca/">
<link rel="canonical" href="https://www.terraincognita.ca/">
<style>*,*::before,*::after{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style>
'''
te = page.index('</title>') + len('</title>')
html = head + page[:te] + '\n' + page[te:].replace('<div class="wrap">', '</head><body>\n<div class="wrap">', 1) + '\n</body></html>\n'

os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'index.html'), 'w').write(html)
updated = max([d.get('checked', '') for d in docs] + [c.get('date', '') for c in changes])
open(os.path.join(out, 'data.json'), 'w').write(json.dumps({
    'name': 'Terra Incognita', 'license': 'CC BY 4.0', 'url': 'https://www.terraincognita.ca/',
    'updated': updated, 'questions': docs, 'changes': changes, 'digests': digests}, ensure_ascii=False, indent=1))
open(os.path.join(out, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\nSitemap: https://www.terraincognita.ca/sitemap.xml\n')
open(os.path.join(out, 'sitemap.xml'), 'w').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'<url><loc>https://www.terraincognita.ca/</loc><lastmod>{updated}</lastmod></url>\n</urlset>\n')
print(f'built {len(docs)} questions, {len(changes)} change entries, updated {updated}')
