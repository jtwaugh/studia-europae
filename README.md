# Studia Europae

An animated atlas of schools and universities in Christian Europe, 800–1900, live at **https://studia.jtwaugh.com**.

The map runs from Iceland to Kazan and down to Egypt, on a relief base with rivers and no political borders. It shows foundings, migrations of masters and students, relocations, mergers, suppressions, destructions, refoundations, confessional changes, reforms, splits and widened access. A timeline plays the centuries, an event log filters by event type and kind of school, and each school has a cited history with the people who studied or taught there. The People tab traces scholars' routes and teacher–student lineages.

## Layout

| Path | What it is |
|---|---|
| `site/` | The deployed static site (`index.html` with the data embedded, `relief.jpg`). Vercel serves this folder. |
| `data/` | Regional source records: institutions, events and residencies, one JSON file per region, and the spec they follow (`SPEC.md`). |
| `cite/` | Citation passes (`cites_*.json`) and people itineraries (`people_*.json`), with their specs and `progress.py`. |
| `build/` | Scripts that project the base map, merge the data and citations, and assemble the page. |

## Rebuilding

The scripts were written in a scratch workspace and still use its absolute paths (`/home/claude/...`). In order:

1. `build/basemap.py` projects Natural Earth coastlines, rivers and lakes plus a shaded relief raster into `basemap.json` and `relief.jpg`.
2. `build/merge.py` merges `data/r*.json` into `data.json`.
3. `build/merge2.py` applies the citation passes and people files, producing `data2.json`.
4. `build/build.py` fills `head.html` + `script.html` with the map and data to make the page.

## Status of the data

This is a working draft compiled with AI assistance and being checked against published sources. Each event and residency carries a status: confirmed, corrected, disputed or unverified. Treat unverified items as leads.
