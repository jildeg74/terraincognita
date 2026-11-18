# Terra Incognita

A living map of what humanity does not know yet: great open scientific questions, linked together, each with what we know, what blocks us, current leads and sources. Seven languages: English, 中文, Español, हिन्दी, العربية, Français, Português.

Website: https://www.terraincognita.ca

## Contents
- `data/questions/` — one JSON file per open question: the source of truth.
- `data/changes/`, `data/digests/` — change log and monthly reports.
- `page/index.html` — page template; `tools/build_site.py` builds `site/` from it and the data.
- `tools/validate.py` — checks every file (7 languages, sources, links). Run automatically by GitHub Actions, which also rebuilds `site/`.
- `site/` — the public website published by Netlify. `site/data.json` holds the full dataset.
- `AGENT.md` — the rules any maintainer (AI or human) must follow. `CONTRIBUTING.md` — how to help.

## How it stays up to date
A research agent re-checks a quarter of the questions every week against recent publications, updates text and sources in all seven languages, and logs every change in `data/changes/`. The project depends on no single AI or person: any capable agent or human can continue the work by following `AGENT.md`. Corrections and new questions are welcome through the form on the website or by pull request.

## Status
First survey prepared with Claude (Anthropic) in November 2026 and checked against the sources listed for each question. Not yet reviewed by domain specialists; researchers who want to review a field can volunteer through the website.

## License
Data and texts: Creative Commons Attribution 4.0 International (CC BY 4.0). Code: MIT.
Please cite using `CITATION.cff`.
