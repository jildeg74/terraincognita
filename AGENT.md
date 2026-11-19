# Instructions for any maintainer agent

This file is written for any AI system (from any company, of any generation) or any human who maintains Terra Incognita. The project must not depend on one model, one company or one person. Everything needed is in this repository.

Read `PROJECT.md` first: it explains the project, its history, decisions, services and accounts. Add a line to its journal (section 9) after any significant change.

## The one absolute rule
**Nothing false, nothing invented.** Every statement must be supported by a source you actually opened and read during this session. If you cannot verify something, do not write it. Leaving a fiche unchanged is always better than changing it on a guess. Never invent a title, an author, a URL, a figure or a date. Never cite a URL you did not open.

## Where things live
- `data/questions/<id>.json` — one open question per file. This is the source of truth.
- `data/changes/<YYYY-MM-DD>.json` — the log of each update session.
- `data/digests/<YYYY-MM>.json` — the monthly report "What moved this month".
- `page/index.html` — the page template. `tools/build_site.py` turns data + template into `site/`.
- `tools/validate.py` — must pass (0 errors) before any commit to `main`. The GitHub Action also runs it and rebuilds `site/`.

## Question format
```json
{
 "d": "P|V|E|M|I|T|H",          // domain: Physics/universe, Life, mind (Esprit), Maths, AI, Earth (Terre), Humanity
 "n": 0,                         // 0 = far from solved, 1 = progress, 2 = close / partly solved, 3 = solved
 "solved": "YYYY-MM-DD",         // only when n = 3: date of the result that settled it
 "links": ["other-id"],          // related questions (must exist)
 "i18n": {"en": {"t": "question", "s": "short label", "known": "...", "block": "...", "leads": "..."}, "fr": {...}, "zh": {...}, "es": {...}, "hi": {...}, "ar": {...}, "pt": {...}},
 "src": [{"t": "exact title of the source", "u": "https://...", "ty": "study"}],
 "sub": [{"en": "...", "fr": "...", "zh": "...", "es": "...", "hi": "...", "ar": "...", "pt": "..."}],
 "rev": [{"name": "Reviewer name", "affil": "Institution"}],
 "checked": "YYYY-MM-DD"
}
```
- All seven languages are mandatory for every text field. English is written first; the other six are faithful translations, never additions.
- `why` (recommended) = why it matters: what would change for people if the question were answered, 1-2 sentences, at most 45 words in English, every consequence supported by a source you opened. `known` = established facts, `block` = what prevents progress, `leads` = active research directions. Short, plain sentences a curious 15-year-old understands.

## "In depth" section (optional, being rolled out)
Each question page can carry a longer section for readers who do research: `i18n.<lang>.detail = {"state": "...", "ideas": "...", "settle": "...", "recent": "..."}` (where things stand, competing ideas, what would settle it, latest developments), with its own numbered source list `dsrc` (1 to 12 entries, same format as `src`).
- About 250 to 350 words in English. Every English sentence ends with at least one citation marker `[n]` pointing to `dsrc[n-1]`, and the sentence must be supported by that source, opened and read in this session. `tools/validate.py` rejects an English sentence without a marker, and any language whose markers differ from the English ones in a section.
- Same plain style as the rest of the fiche. Numbers, dates and names exactly as in the source. Results from a preprint or a press release are described as such.
- This text appears only on the question pages, not on the map (the map stays light).
- Roll-out: about 10 questions per weekly session, starting with those that have none (`dsrc` absent), until all questions have one. Each batch goes through the independent verification like any other change.

## Sources
- 1 to 3 per question, `https` only, title copied exactly from the page.
- Types `ty`: `study` (peer-reviewed article), `reference` (academic review, textbook, official problem statement), `preprint` (arXiv, bioRxiv, medRxiv… not yet peer-reviewed), `official` (agency, intergovernmental body), `institution` (university, lab, observatory), `press` (journalism), `company`, `encyclopedia`.
- Aim for at least one `study` or `reference` per question. Prefer primary sources (the paper itself) over articles about it.
- A source cannot carry a claim it does not contain. Recent results announced only by preprint or press must be described as such ("a 2026 preprint reports…").

## Update session (weekly by default)
0. First read `OPEN_ISSUES.md` and settle as many listed items as possible (source or remove), then update that file.
1. Pick the questions to check. Default: the quarter whose index (alphabetical order of ids) satisfies `index % 4 == ISO week % 4`. As the map grows, check fast-moving fields (AI, medicine, climate) more often and stable ones (pure maths) less often; record this choice in the change log.
2. For each: search for important developments since `checked`, open and read the sources, update text in 7 languages only if a verified fact changed, improve sources, set `checked` to today.
3. Add 3 sub-questions (7 languages) to questions that have none, only if they are real research sub-questions found in the sources.
4. Write `data/changes/<today>.json`: `{"date": "...", "items": [{"q": "<id>", "f": "known|block|leads|src|sub|n"}, {"k": "sources", "n": <count checked>}]}`.
5. During the first 7 days of a month, write `data/digests/<previous month>.json`: `{"month": "YYYY-MM", "i18n": {"en": {"body": "..."}, ...7 languages}}` summarising verified changes of the previous month.
6. **Independent verification (mandatory before every publication).** A second agent (or person) that did not write the changes reviews `git diff`: it opens every new or changed source itself, checks the title and type, checks that each new or changed sentence (in English, and that the 6 translations say the same) is supported by a source it opened, and checks each new sub-question. Anything it cannot confirm is reverted to the previous version (`git checkout -- <file>` or a manual edit). Only what it approves is kept. Its findings go in the final report.
7. Run `python3 tools/validate.py` (must show 0 errors), then `python3 tools/build_site.py page/index.html data/questions data/changes site data/digests`.
8. Commit with a message saying what changed and push to `main`. Netlify publishes `site/` automatically.

## Growing the map
During the first update session of each month (the one that writes the monthly digest), add **up to 2 new questions** (consolidation phase, decided 2026-11-19: the existing fiches come first). Add none at all unless every item of `OPEN_ISSUES.md` that can be settled has been settled; items that only wait for research not yet published do not block. Priority: (1) serious proposals received from the public, (2) the domains with the fewest questions, (3) open questions that recent research has made prominent. Never add a question just to reach the number: zero is fine if nothing qualifies. Each new question must meet every rule below, have 3 sub-questions, and pass the independent verification; otherwise it is not added. Log each one in the change log as `{"q": "<id>", "f": "new"}` and mention it in the monthly digest.

## Adding a new question
Only for a genuine open question recognized in the scientific literature, not already on the map, with at least one `study` or `reference` source. Give it a short lowercase id with hyphens, link it to existing related questions, and add the reverse links.

## When a question is solved
Never delete it. A question is solved only when the answer is accepted by the field, shown in peer-reviewed work (or, in mathematics, a proof accepted by experts), not by a single announcement or preprint. Then set `n` to 3, add `"solved"` with the date of the decisive result, rewrite `known` to say what was found and by whom, `block` to say what remains open around it, `leads` to the new questions it opens, cite the decisive paper, and log `{"q": "<id>", "f": "n"}` in the change log. Solved questions stay on the map as conquered territory.

## Independent verification
When a large batch is produced (many fiches at once), a second agent or person who did not write it must check every claim and every source before it is merged. Reject anything that cannot be confirmed.
