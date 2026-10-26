# People pass: itineraries and teacher–student links, with citations

The atlas will get a "people" view: pick a person and see their life path across Europe (birth, studies, teaching posts, travels, exile, death) and who taught them and whom they taught, at which institution. Every stop and every link needs a citation to a reputable source.

Your input is a roster file (a list of people, each with an `id`, `name` and their known residencies `stints` at institutions in the atlas, each with a stint key `k`). Institution ids (`inst`) refer to the atlas; the full list of institution ids, names and cities is in /home/claude/cite/institutions.json — use those ids whenever a stop or a teaching link happened at an atlas institution.

## Reputable sources
Same rules as /home/claude/cite/CITE_SPEC.md (read its source list). Especially useful: Stanford Encyclopedia of Philosophy, MacTutor, Galileo Project, Mathematics Genealogy Project (for doctoral advisor links, 17th–19th c.), Deutsche Biographie (NDB/ADB), Treccani, Britannica, Catholic Encyclopedia (newadvent.org), Oxford DNB abstracts, Complete Dictionary of Scientific Biography (encyclopedia.com), Historisches Lexikon der Schweiz, Repertorium Academicum Germanicum. Do not cite Wikipedia unless nothing else exists (then tier 3).

## Output (valid JSON) to the file named in your task
```json
{
  "era": "a",
  "sources": {"pa-001": {"title": "Thomas Aquinas", "publisher": "Stanford Encyclopedia of Philosophy", "url": "https://plato.stanford.edu/entries/aquinas/", "tier": 2}},
  "people": [
    {
      "id": "thomas-aquinas",
      "name": "Thomas Aquinas",
      "born": 1225, "born_approx": true, "died": 1274, "died_approx": false,
      "bio": "One plain sentence on who they were.",
      "fields": ["theology", "philosophy"],
      "src": ["pa-001"],
      "stops": [
        {"from": 1225, "to": 1225, "approx": true, "kind": "birth", "place": "Roccasecca", "lat": 41.55, "lon": 13.67, "inst": null, "note": "", "src": ["pa-001"]},
        {"from": 1239, "to": 1244, "kind": "study", "place": "Naples", "lat": 40.8518, "lon": 14.2681, "inst": "u-naples", "note": "Studied arts at the studium generale.", "src": ["pa-001"]},
        {"from": 1245, "to": 1248, "kind": "study", "place": "Paris", "lat": 48.8503, "lon": 2.3446, "inst": "u-paris", "note": "Studied under Albertus Magnus.", "src": ["pa-001"]},
        {"from": 1274, "to": 1274, "kind": "death", "place": "Fossanova", "lat": 41.44, "lon": 13.20, "inst": null, "note": "", "src": ["pa-001"]}
      ],
      "teachers": [
        {"id": "albertus-magnus", "inst": "u-paris", "place": "Paris", "from": 1245, "to": 1252, "kind": "teacher", "src": ["pa-001"]}
      ]
    }
  ]
}
```
- `kind` for stops: `birth`, `study`, `teach` (incl. professorships, lecturing), `office` (court, church or government post, rector without teaching), `travel` (journeys, study trips, pilgrimages, missions), `exile`, `research` (observatory, library or academy work outside teaching), `death`. Stops must be in chronological order and cover the person's main moves; 4–12 stops is typical. Every roster stint should be reflected by a stop with that `inst` (correct its years if sources disagree and say so in the stop `note`).
- `teachers`: direct teacher–student relations only (studied under, doctoral/thesis advisor, apprenticed to, attended the lectures of — say which in `kind`: `teacher`, `doctoral advisor`, `mentor`, `attended lectures`). Record the link on the STUDENT. `inst` where it happened (atlas id) or null with `place`. Teachers may be people not in your roster: then ALSO add them to `people` as a full record (with stops) if they are notable, or as a minimal record (id, name, born, died, bio, src, stops: [] ) otherwise.
- Students of roster people: if you know well-documented students who are themselves notable, add those students as people records with the `teachers` link pointing back. Prefer links that connect people who are already on the roster (any era roster file /home/claude/cite/roster_*.json) — that is what makes the lineage network useful. Aim for at least one teacher link for most people where documented.
- Person ids: lowercase ASCII slug of the common English name, hyphen-separated (e.g. `albertus-magnus`, `philipp-melanchthon`, `carl-friedrich-gauss`). For people on any roster file, use the roster id exactly. Check /home/claude/cite/roster_*.json before inventing an id for a teacher.
- Coordinates: town centre, 2–4 decimals.
- Source ids: `p<era>-NNN`.
- Nothing invented: if a stop or link cannot be sourced, leave it out. Uncertain years → `approx: true`.

Write the file progressively; validate JSON and that every `src` id exists in `sources` and every `inst` exists in institutions.json before finishing. Reply with counts (people, stops, teacher links) and notable gaps (under 100 words).
