# Dataset spec: European / Christian higher-education institutions, 800–1900 CE

Scope: Latin-Christian Europe plus Byzantine/Orthodox institutions. Map extent: Iceland in the west, Kazan in the east, Egypt in the south. Exclude Islamic and Jewish institutions (madrasas, yeshivot) for now.

Write ONE JSON file (UTF-8, valid JSON, no comments) with exactly this shape:

```json
{
  "region": "short region name",
  "institutions": [ ... ],
  "events": [ ... ],
  "thinkers": [ ... ]
}
```

## Institution

```json
{
  "id": "u-bologna",
  "name": "University of Bologna",
  "alt": ["Studium of Bologna", "Alma Mater Studiorum"],
  "type": "university",
  "locations": [
    {"from": 1088, "city": "Bologna", "lat": 44.4964, "lon": 11.3533}
  ],
  "modern_country": "Italy",
  "start": 1088, "start_approx": true,
  "end": null, "end_approx": false,
  "founding_mode": "spontaneous",
  "summary": "2–3 sentences: what it was, why it mattered.",
  "notes": "Optional: disputed dates, continuity questions. Empty string if none."
}
```

- `locations`: one entry per seat. If the institution moved, add an entry per move with the year it arrived (`from`). Coordinates of the historic town centre, 4 decimals.
- `end`: year it ceased to exist (closed, suppressed for good, merged away, or turned into something else that gets its own record). `null` if it survived past 1900. If suppressed and later refounded under the same identity, keep ONE institution and record both events; `end` stays null if it survived.
- `start`/`end` approximate → set the `_approx` flag.

### `type` (exactly one)
- `palace` – palace/court schools (Carolingian palace school, royal court schools).
- `cathedral` – cathedral, collegiate and monastic schools (pre-university Latin schooling of the higher sort: Chartres, Reims, Laon, Fulda, St Gall, etc.).
- `byzantine` – Byzantine and Orthodox higher schools and academies (Magnaura, Pandidakterion, Patriarchal Academy, Kyiv-Mohyla, Slavic-Greek-Latin Academy, Ionian Academy).
- `professional` – *studia particularia* and single-faculty higher schools before/alongside universities: Salerno medicine, Montpellier medicine before 1289, law schools that never became studia generalia, royal colleges of surgeons/physicians that taught.
- `university` – *studium generale* / university (incl. Orthodox-country universities after c. 1750 that follow the university model).
- `jesuit` – Jesuit colleges/academies teaching at university level that were NOT full universities (Collegio Romano belongs here until it is a university; Jesuit academies like Vilnius before 1579 or Olomouc colleges, Pont-à-Mousson if not counted as university, etc. Use judgement; if it held university privileges, it is `university`).
- `protestant` – Protestant academies, Hohe Schulen, gymnasia illustria, Huguenot academies (Geneva 1559, Lausanne 1537, Herborn, Saumur, Sedan, Strasbourg Gymnasium before university status, Dissenting academies in England).
- `technical` – polytechnics, mining and forestry academies, engineering, veterinary, military-engineering and other specialist higher schools incl. French grandes écoles (École polytechnique, ENS, Ponts et Chaussées, Freiberg, Schemnitz, ETH, TH Karlsruhe…).

### `founding_mode` (exactly one)
`spontaneous` (ex consuetudine, grew up), `papal`, `imperial`, `royal`, `princely` (territorial prince, duke, elector, bishop as prince), `municipal` (city council), `ecclesiastical` (bishop, chapter, order, abbey — not papal), `state` (modern state ministry/ parliament), `private` (private society/individual), `secession` (formed by migrating masters/students), `other`.

## Event

```json
{
  "id": "u-bologna-1158-charter",
  "inst": "u-bologna",
  "year": 1158, "approx": false,
  "type": "charter",
  "title": "Authentica Habita",
  "desc": "1–2 sentences, specific.",
  "from_inst": null,
  "related": []
}
```

### `type` (exactly one)
- `founding` – institution begins (first teaching, bull, charter, or formal opening; say which in desc). EVERY institution must have exactly one `founding` event whose year equals `start`.
- `charter` – recognition or major privilege granted after founding: papal confirmation, ius ubique docendi, royal/imperial privileges, statutes.
- `migration` – masters/students secede from one institution and found or swell another. Attach to the DESTINATION institution; put the source in `from_inst`.
- `relocation` – the institution itself moves seat (must match a new `locations` entry with the same year).
- `merger` – two or more institutions combine; attach to the surviving/new one, put the absorbed ones in `related`. The absorbed institution gets `end` = that year.
- `suppression` – closed/abolished by authority (state, church, revolution, Napoleon, Jesuit suppression 1773).
- `destruction` – physical destruction or collapse by war, fire, plague, sack, siege, conquest.
- `refoundation` – reopened or restored after suppression/decay.
- `confessional` – change of confession or religious control (Reformation conversion, Counter-Reformation, Jesuit takeover, end of religious tests).
- `reform` – structural reorganization: new statutes, new faculties, state reform (Humboldtian, Napoleonic, Theresian, Pombaline, Spanish Bourbon), secularization, language of instruction changes.
- `split` – institution divides along national/linguistic/confessional lines (Prague 1882).
- `access` – change in who may study: admission of women, removal of religious tests for students, etc.

`related`: ids of other institutions involved (any region). Event `id` = `<inst>-<year>-<type>` (add `-2` etc. if duplicate).

Cover the major events of each institution's history up to 1900, not only founding. Aim for 2–6 events per significant institution, 1–2 for minor ones.

## Thinkers (famous people in residence)

```json
{"name": "Irnerius", "inst": "u-bologna", "from": 1088, "to": 1125, "approx": true, "role": "taught Roman law", "note": "Founder of the glossator school."}
```
Only well-known figures (scholars, scientists, theologians, writers, reformers) whose time at the institution is reasonably documented. `role`: studied / taught / rector / founded / etc. in a few words. Several entries for one person at different institutions are fine (each region covers its own institutions). Aim for 3–10 per major university, 0–2 for minor ones.

## ID conventions (shared across all regions — use these exact ids for cross-references)
Prefix by type: `u-` university, `c-` cathedral/monastic, `p-` palace, `b-` byzantine/orthodox, `m-` professional, `j-` jesuit, `a-` protestant academy, `t-` technical. Then lowercase ASCII city (and a suffix if needed).

Canonical ids for frequently cross-referenced institutions:
u-bologna, u-paris, u-oxford, u-cambridge, u-padua, u-vicenza, u-vercelli, u-arezzo, u-siena, u-naples, u-rome (Studium Urbis / La Sapienza), u-montpellier, m-montpellier (medicine before 1289), m-salerno, u-toulouse, u-orleans, u-angers, u-salamanca, u-palencia, u-valladolid, u-lisbon-coimbra (Portuguese university that alternated Lisbon/Coimbra until 1537, then Coimbra), u-prague (Charles University until 1882), u-prague-czech, u-prague-german, u-krakow, u-vienna, u-heidelberg, u-cologne, u-erfurt, u-leipzig, u-rostock, u-wittenberg, u-halle, u-halle-wittenberg, u-frankfurt-oder, u-breslau, u-ingolstadt-munich (Ingolstadt→Landshut→Munich), u-leuven, u-strasbourg, u-dorpat, u-vilnius, u-konigsberg, u-st-andrews, u-glasgow, u-aberdeen-kings, u-aberdeen-marischal, u-aberdeen, u-edinburgh, u-dublin, u-uppsala, u-copenhagen, u-lund, u-turku-helsinki (Åbo→Helsinki), u-moscow, u-kazan, u-athens, b-patriarchal-academy, b-magnaura, b-pandidakterion, p-aachen, a-geneva, j-collegio-romano, t-polytechnique, t-ens.

## Regional ownership (avoid duplicates)
Each agent only creates institutions in its own region; it may REFERENCE ids from other regions in `from_inst`/`related`.
- Region 1 Italy & Malta (incl. Sicily, Sardinia, Corsica).
- Region 2 Iberia.
- Region 3 France, Low Countries, Switzerland (NOT Strasbourg).
- Region 4 German lands & Austria incl. Strasbourg, Prussia (Königsberg), Alsace, Silesia (Breslau). NOT Bohemia/Moravia.
- Region 5 British Isles, Scandinavia, Iceland, Finland.
- Region 6 Bohemia/Moravia, Poland-Lithuania, Hungary (incl. Slovakia, Transylvania), Croatia/Slovenia, Baltic provinces, Russia, Ukraine, Belarus, Romanian principalities.
- Region 7 Byzantium & Orthodox Balkans (Constantinople, Greece, Ionian Is., Serbia, Bulgaria, Cyprus, Mount Athos, Egypt/Levant Christian institutions) — AND all `palace` and `cathedral` schools of Latin Europe 800–1200 everywhere (Region 7 owns every `p-` and `c-` record; other regions must not create them).

Accuracy beats volume. Use well-established dates; set `approx` when dates are conventional or disputed and explain in notes. Do not invent thinkers' stays.
