# Citation pass: verify and source one slice of the atlas dataset

You are checking a slice of a dataset of European schools and universities, 800–1900, against reputable published sources, and attaching citations. Your slice is a JSON file with `institutions`, `events` and `thinkers` (residencies). Do NOT edit the slice. Write your results to the output file named in your task.

## What counts as a reputable source (in rough order of preference)
1. The institution's own official history pages (university website "history"/"Geschichte"/"storia" pages, archives).
2. Scholarly reference works: Encyclopaedia Britannica (britannica.com), Catholic Encyclopedia 1913 (newadvent.org), Treccani (treccani.it), Deutsche Biographie / NDB / ADB (deutsche-biographie.de), Historisches Lexikon der Schweiz (hls-dhs-dss.ch), Oxford DNB abstracts, Dictionary of Irish Biography, Svenskt biografiskt lexikon, Polski Słownik Biograficzny entries online, Real Academia de la Historia DB~e (dbe.rah.es), Stanford Encyclopedia of Philosophy (plato.stanford.edu), MacTutor History of Mathematics (mathshistory.st-andrews.ac.uk), Galileo Project (galileo.rice.edu), Dictionary of Scientific Biography mirrors (encyclopedia.com "Complete Dictionary of Scientific Biography"), Repertorium Academicum Germanicum (rag-online.org), Mathematics Genealogy Project.
3. Digitized scholarly books: Rashdall, *The Universities of Europe in the Middle Ages* (archive.org), de Ridder-Symoens & Rüegg *A History of the University in Europe*, Google Books previews of university histories.
4. National heritage/government sites, museum pages.
Avoid: Wikipedia as a cited source (you may use it to find leads and its references, then cite the underlying source), blogs, tourism sites, AI-generated pages, SEO content farms. If after real effort only Wikipedia supports a claim, you may cite it but mark `"tier": 3`.

## Method (be efficient)
- For each institution, find 1–3 strong sources that cover its overall history (official history page + one reference work is ideal). Fetch them (WebFetch) and check every event of that institution against them. Most events will be confirmed by these same sources.
- Search separately only for events the general sources do not cover, and for disputed dates.
- For residencies (thinkers), use one good biography source per person (SEP, MacTutor, Britannica, NDB, Treccani, Galileo Project, DSB) and check years and role.
- Budget: aim to finish. Prioritize universities and major schools first, then minor schools. If you run out of budget, mark the rest `unverified` rather than guessing.
- Run independent searches in parallel (several WebSearch calls in one turn).

## Output file shape (valid JSON)
```json
{
  "group": "it",
  "sources": {
    "it-001": {"title": "History of the University", "publisher": "Università di Bologna", "url": "https://www.unibo.it/en/university/who-we-are/our-history", "tier": 1},
    "it-002": {"title": "University of Bologna", "publisher": "Encyclopaedia Britannica", "url": "https://www.britannica.com/topic/University-of-Bologna", "tier": 2}
  },
  "institutions": {
    "u-bologna": {"src": ["it-001","it-002"], "fix": {}, "note": ""}
  },
  "events": {
    "u-bologna-1158-charter": {"status": "confirmed", "src": ["it-002"], "fix": {}, "note": ""}
  },
  "thinkers": {
    "th123": {"status": "corrected", "src": ["it-014"], "fix": {"from": 1592, "to": 1610}, "note": "Taught at Padua 1592–1610 per Galileo Project."}
  }
}
```
- Source ids: `<group>-NNN`, unique within your file. `tier`: 1 official/primary institution, 2 scholarly reference, 3 weaker (only when nothing better).
- `status` for events and thinkers: `confirmed` (source supports it as stated, approx dates OK if marked approx), `corrected` (source supports a different value: put the corrected fields in `fix`), `unverified` (no reputable source found), `doubtful` (sources contradict it or it seems wrong; explain in `note`), `remove` (clearly false or a duplicate).
- `fix` may contain for events: `year`, `approx`, `title`, `desc`, `type`; for thinkers: `from`, `to`, `approx`, `role`; for institutions: `start`, `start_approx`, `end`, `end_approx`, `name`, `summary`, `note`, `locations` (full replacement list of {from, city, lat, lon}).
- Every key in `events` and `thinkers` must be an id/`k` from your slice. Include EVERY event and EVERY thinker entry of the slice in the output (use `unverified` with empty src if you could not check it).
- `note`: short, plain English, for the reader of the atlas. No mention of "slice", "spec", "region" or the dataset process.

Write the file progressively (e.g. after each batch of institutions) so work is not lost; the final file must be valid JSON. Validate with python before finishing: all slice event ids and thinker k's present, all src ids defined in `sources`. Reply with counts by status and any systematic problems you found (under 120 words).
