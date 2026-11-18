# Terra Incognita

A living map of what humanity does not know yet: great open scientific questions, linked together, each with what we know, what blocks us, current leads and sources. Seven languages: English, 中文, Español, हिन्दी, العربية, Français, Português.

Website: https://www.terraincognita.ca

## Contents
- `site/` — the public website (static, published by Netlify). `site/data.json` holds the full dataset.
- `tools/build_site.py` — rebuilds the site from the database export.

## How it stays up to date
A research agent re-checks a quarter of the questions every week against recent publications, updates text and sources in all seven languages, and logs every change in `site/data.json` (`changes`). Corrections and new questions are welcome through the form on the website.

## Status
First survey prepared with Claude (Anthropic) in November 2026 and checked against the sources listed for each question. Not yet reviewed by domain specialists; researchers who want to review a field can volunteer through the website.

## License
Data and texts: Creative Commons Attribution 4.0 International (CC BY 4.0). Code: MIT.
Please cite using `CITATION.cff`.
