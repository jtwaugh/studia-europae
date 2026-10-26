"""Apply citation passes and people passes to data.json -> data2.json (whatever files exist so far)."""
import json, glob, re, unicodedata, collections, os
from pyproj import Transformer
bm = json.load(open('/home/claude/build/basemap.json')); P = bm['proj']
F = Transformer.from_crs("EPSG:4326", P['def'], always_xy=True)
def xy(lon, lat):
    x, y = F.transform(lon, lat); return round((x - P['X0']) / P['S'], 1), round((P['Y1'] - y) / P['S'], 1)
def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

d = json.load(open('/home/claude/build/data.json'))
I = {i['id']: i for i in d['inst']}
E = {e['id']: e for e in d['ev']}
for n, t in enumerate(d['th']): t['k'] = f'th{n}'; t['p'] = slug(t['n'])
TH = {t['k']: t for t in d['th']}
SRC = {}
report = collections.Counter(); problems = []

def addsrc(sid, s):
    if not isinstance(s, dict) or not s.get('url'): return False
    SRC[sid] = {'t': s.get('title', ''), 'p': s.get('publisher', ''), 'u': s['url'], 'tier': s.get('tier', 2)}
    return True

# ---------- citation passes ----------
for f in sorted(glob.glob('/home/claude/cite/cites_*.json')):
    try: c = json.load(open(f))
    except Exception as ex: problems.append(f'{f} unreadable: {ex}'); continue
    ok = {sid for sid, s in c.get('sources', {}).items() if addsrc(sid, s)}
    S = lambda lst: [s for s in (lst or []) if s in ok]
    for iid, r in c.get('institutions', {}).items():
        i = I.get(iid)
        if not i: continue
        i['src'] = S(r.get('src')); fx = r.get('fix') or {}
        for a, b in [('start', 's'), ('start_approx', 'sa'), ('end', 'e'), ('end_approx', 'ea'), ('name', 'n'), ('summary', 'sum'), ('note', 'note')]:
            if a in fx and fx[a] is not None or (a == 'end' and 'end' in fx): i[b] = fx[a]
        if fx.get('locations'):
            try: i['L'] = [{'f': l['from'], 'c': l['city'], 'x': xy(l['lon'], l['lat'])[0], 'y': xy(l['lon'], l['lat'])[1], 'lat': l['lat'], 'lon': l['lon']} for l in sorted(fx['locations'], key=lambda l: l['from'])]
            except Exception as ex: problems.append(f'{iid} bad locations fix {ex}')
        if r.get('note'): i['cnote'] = r['note']
    for eid, r in c.get('events', {}).items():
        e = E.get(eid)
        if not e: problems.append(f'{f}: unknown event {eid}'); continue
        st = r.get('status', 'unverified'); report['ev:' + st] += 1
        e['st'] = st; e['src'] = S(r.get('src'))
        fx = r.get('fix') or {}
        if st in ('corrected', 'doubtful', 'confirmed'):
            for a, b in [('year', 'y'), ('approx', 'a'), ('title', 'ti'), ('desc', 'd'), ('type', 't')]:
                if a in fx and fx[a] is not None: e[b] = fx[a]
        if r.get('note'): e['cn'] = r['note']
    for k, r in c.get('thinkers', {}).items():
        t = TH.get(k)
        if not t: problems.append(f'{f}: unknown thinker {k}'); continue
        st = r.get('status', 'unverified'); report['th:' + st] += 1
        t['st'] = st; t['src'] = S(r.get('src'))
        fx = r.get('fix') or {}
        for a, b in [('from', 'f'), ('to', 'to'), ('approx', 'a'), ('role', 'r')]:
            if a in fx and fx[a] is not None: t[b] = fx[a]
        if r.get('note'): t['cn'] = r['note']

d['ev'] = [e for e in d['ev'] if e.get('st') != 'remove']
d['th'] = [t for t in d['th'] if t.get('st') != 'remove']
# keep founding consistent with start after fixes
for e in d['ev']:
    if e['t'] == 'founding' and I[e['i']]['s'] != e['y']: I[e['i']]['s'] = e['y']
d['ev'].sort(key=lambda e: e['y'])

# ---------- people passes ----------
people = {}
KINDS = {'birth', 'study', 'teach', 'office', 'travel', 'exile', 'research', 'death'}
def stop(s, ok):
    try: x, y = xy(float(s['lon']), float(s['lat']))
    except Exception: return None
    k = s.get('kind', 'other'); k = k if k in KINDS else 'travel'
    inst = s.get('inst') if s.get('inst') in I else None
    return {'f': s.get('from'), 'to': s.get('to', s.get('from')), 'a': bool(s.get('approx')), 'k': k, 'pl': s.get('place', ''),
            'x': x, 'y': y, 'i': inst, 'no': s.get('note', ''), 'src': [q for q in s.get('src', []) if q in ok]}
for f in sorted(glob.glob(os.environ.get('PEOPLEGLOB','/home/claude/cite/people_*.json'))):
    try: c = json.load(open(f))
    except Exception as ex: problems.append(f'{f} unreadable: {ex}'); continue
    ok = {sid for sid, s in c.get('sources', {}).items() if addsrc(sid, s)}
    for p in c.get('people', []):
        pid = p.get('id') or slug(p.get('name', ''))
        if not pid: continue
        stops = [s for s in (stop(s, ok) for s in p.get('stops', [])) if s and s['f'] is not None]
        stops.sort(key=lambda s: (s['f'], 0 if s['k'] == 'birth' else 2 if s['k'] == 'death' else 1))
        te = [{'id': t['id'], 'i': t.get('inst') if t.get('inst') in I else None, 'pl': t.get('place', ''), 'f': t.get('from'), 'to': t.get('to'),
               'k': t.get('kind', 'teacher'), 'no': t.get('note', ''), 'src': [q for q in t.get('src', []) if q in ok]} for t in p.get('teachers', []) if t.get('id')]
        rec = {'id': pid, 'n': p.get('name', pid), 'b': p.get('born'), 'ba': bool(p.get('born_approx')), 'd': p.get('died'), 'da': bool(p.get('died_approx')),
               'bio': p.get('bio', ''), 'fl': p.get('fields', []), 'src': [q for q in p.get('src', []) if q in ok], 'stops': stops, 'te': te}
        old = people.get(pid)
        if old:  # merge: keep the richer record, union teachers
            if len(stops) > len(old['stops']): rec['te'] = rec['te'] + [t for t in old['te'] if t['id'] not in {x['id'] for x in rec['te']}]; people[pid] = rec
            else: old['te'] += [t for t in te if t['id'] not in {x['id'] for x in old['te']}]
        else: people[pid] = rec

# fallback people from residencies (no sourced path yet)
byp = collections.defaultdict(list)
for t in d['th']: byp[t['p']].append(t)
for pid, ts in byp.items():
    if pid in people: continue
    stops = []
    for t in sorted(ts, key=lambda t: t['f'] or t['to'] or 0):
        i = I[t['i']]; L = i['L'][0]
        for l in i['L']:
            if l['f'] <= (t['f'] or 0): L = l
        role = (t['r'] or '').lower()
        k = 'teach' if any(w in role for w in ('taught', 'teach', 'professor', 'lectur', 'chair', 'master', 'regent', 'rector', 'dean', 'tutor')) else 'study' if 'stud' in role or 'student' in role or 'matric' in role else 'office'
        stops.append({'f': t['f'] or t['to'], 'to': t['to'] or t['f'], 'a': t['a'], 'k': k, 'pl': L['c'], 'x': L['x'], 'y': L['y'], 'i': t['i'], 'no': t['r'], 'src': t.get('src', [])})
    people[pid] = {'id': pid, 'n': ts[0]['n'], 'b': None, 'ba': False, 'd': None, 'da': False, 'bio': '', 'fl': [], 'src': [], 'stops': stops, 'te': [], 'fallback': True}

# ALIAS: duplicate ids for the same person
ALIAS={'petrarch':'francesco-petrarca','samuel-von-pufendorf':'samuel-pufendorf'}
for f in glob.glob('/home/claude/cite/people_*.json'):
    try:
        for p in json.load(open(f)).get('people',[]):
            if p.get('same_as') and p.get('id') and p['same_as']!=p['id']: ALIAS[p['id']]=p['same_as']
    except Exception: pass
for a,b in ALIAS.items():
    if a in people and b in people:
        A,B=people.pop(a),people[b]
        if len(A['stops'])>len(B['stops']): A['id']=b; A['te']+= [x for x in B['te'] if x['id'] not in {y['id'] for y in A['te']}]; people[b]=A
        else: B['te']+= [x for x in A['te'] if x['id'] not in {y['id'] for y in B['te']}]
    elif a in people: people[b]=people.pop(a); people[b]['id']=b
for p in people.values():
    for x in p['te']: x['id']=ALIAS.get(x['id'],x['id'])
for t in d['th']: t['p']=ALIAS.get(t['p'],t['p'])
# drop teacher links to unknown people, self links
for p in people.values():
    p['te'] = [t for t in p['te'] if t['id'] in people and t['id'] != p['id']]
    if p['b'] is None and p['stops']: p['b0'] = p['stops'][0]['f']
# FIELDGROUPS: normalise free-text fields into a few filterable groups
FG = {'Theology': ['theology','religion','scripture','mysticism','church','canon law','hebrew'],
      'Philosophy': ['philosophy','logic','natural philosophy','humanism','political thought','psychology'],
      'Law & politics': ['law','politics','government','political economy','economics','diplomacy','criminology','sociology','statistics','feminism'],
      'Medicine': ['medicine','anatomy','surgery','physiology','psychiatry','histology','embryology','obstetrics','neurology','immunology','neuroscience'],
      'Mathematics': ['mathematics','geodesy','statistics'],
      'Astronomy & physics': ['astronomy','physics','optics','cosmography','astrology','microscopy'],
      'Chemistry & earth': ['chemistry','alchemy','mineralogy','geology','geography','cartography'],
      'Life sciences': ['botany','zoology','biology','natural history','natural science','genetics','anthropology'],
      'Letters & history': ['history','literature','poetry','philology','linguistics','rhetoric','grammar','classics','greek','languages','translation','oriental languages','art history','criticism','archaeology','liberal arts','education','music','music theory'],
      'Engineering': ['engineering','architecture','exploration']}
for p in people.values():
    fl = [f.lower() for f in p['fl']]
    p['fg'] = [g for g, ks in FG.items() if any(f in ks for f in fl)]
d['people'] = sorted(people.values(), key=lambda p: (p['b'] or p.get('b0') or 0))
d['src'] = SRC
json.dump(d, open('/home/claude/build/data2.json', 'w'), ensure_ascii=False, separators=(',', ':'))
links = sum(len(p['te']) for p in people.values())
print('sources', len(SRC), 'people', len(people), 'with path', sum(not p.get('fallback') for p in people.values()), 'teacher links', links)
print(dict(report)); print(len(problems), 'problems'); print('\n'.join(problems[:30]))
