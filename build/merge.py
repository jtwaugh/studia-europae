import json, glob, sys, collections, os
from pyproj import Transformer
bm = json.load(open('/home/claude/build/basemap.json'))
P = bm['proj']
F = Transformer.from_crs("EPSG:4326", P['def'], always_xy=True)
def xy(lon, lat):
    x, y = F.transform(lon, lat)
    return round((x - P['X0']) / P['S'], 1), round((P['Y1'] - y) / P['S'], 1)

INST_TYPES = ['university','cathedral','palace','byzantine','professional','jesuit','protestant','technical']
EV_TYPES = ['founding','charter','migration','relocation','merger','suppression','destruction','refoundation','confessional','reform','split','access']
MODES = ['spontaneous','papal','imperial','royal','princely','municipal','ecclesiastical','state','private','secession','other']

insts, evs, ths = {}, [], []
problems = []
for f in sorted(glob.glob(os.environ.get('DATAGLOB','/home/claude/data/r*.json'))):
    try:
        d = json.load(open(f))
    except Exception as e:
        problems.append(f'{f}: unreadable {e}'); continue
    reg = d.get('region', f)
    for i in d['institutions']:
        if i['id'] in insts:
            problems.append(f"dup inst {i['id']} in {f}"); continue
        if i.get('type') not in INST_TYPES: problems.append(f"bad type {i['id']} {i.get('type')}")
        locs = []
        for l in sorted(i['locations'], key=lambda l: l['from']):
            x, y = xy(l['lon'], l['lat'])
            locs.append({'f': l['from'], 'c': l['city'], 'x': x, 'y': y, 'lat': l['lat'], 'lon': l['lon']})
        insts[i['id']] = {
            'id': i['id'], 'n': i['name'], 'alt': i.get('alt') or [], 't': i['type'], 'L': locs,
            'cc': i.get('modern_country', ''), 's': i['start'], 'sa': bool(i.get('start_approx')),
            'e': i.get('end'), 'ea': bool(i.get('end_approx')), 'm': i.get('founding_mode', 'other'),
            'sum': i.get('summary', ''), 'note': i.get('notes', ''), 'reg': reg}
    for e in d['events']:
        evs.append({'id': e['id'], 'i': e['inst'], 'y': e['year'], 'a': bool(e.get('approx')), 't': e['type'],
                    'ti': e.get('title', ''), 'd': e.get('desc', ''), 'fr': e.get('from_inst'),
                    'rel': e.get('related') or []})
    for t in d.get('thinkers', []):
        ths.append({'n': t['name'], 'i': t['inst'], 'f': t.get('from'), 'to': t.get('to'), 'a': bool(t.get('approx')),
                    'r': t.get('role', ''), 'no': t.get('note', '')})

# validation & cleanup
ids = set(insts)
seen = set(); clean = []
for e in evs:
    if e['i'] not in ids: problems.append(f"event {e['id']} -> missing inst {e['i']}"); continue
    if e['t'] not in EV_TYPES: problems.append(f"event {e['id']} bad type {e['t']}"); continue
    if not (400 <= e['y'] <= 1900): problems.append(f"event {e['id']} year {e['y']} out of range"); continue
    if e['fr'] and e['fr'] not in ids: problems.append(f"event {e['id']} from_inst {e['fr']} unknown"); e['fr'] = None
    bad = [r for r in e['rel'] if r not in ids]
    if bad: problems.append(f"event {e['id']} related unknown {bad}")
    e['rel'] = [r for r in e['rel'] if r in ids]
    k = e['id']
    n = 2
    while e['id'] in seen: e['id'] = f'{k}-{n}'; n += 1
    seen.add(e['id']); clean.append(e)
# merger events recorded on the absorbed school: move them to the surviving one
for e in clean:
    if e['t']=='merger' and e['rel']:
        me=insts[e['i']]; tgt=insts[e['rel'][0]]
        if me['e'] is not None and abs(me['e']-e['y'])<=1 and (tgt['e'] is None or tgt['e']>e['y']) and tgt['s']<=e['y']:
            e['rel']=[e['i']]+e['rel'][1:]; e['i']=tgt['id']
_k=set(); _c=[]
for e in clean:
    k=(e['y'],e['t'],e['i'],tuple(sorted(e['rel'])),e['fr'])
    if k in _k: continue
    _k.add(k); _c.append(e)
clean=_c
evs = sorted(clean, key=lambda e: (e['y'], EV_TYPES.index(e['t'])))
fc = collections.Counter(e['i'] for e in evs if e['t'] == 'founding')
for i in insts.values():
    if fc[i['id']] != 1: problems.append(f"inst {i['id']} has {fc[i['id']]} founding events")
ths2 = []
for t in ths:
    if t['i'] not in ids: problems.append(f"thinker {t['n']} -> missing inst {t['i']}"); continue
    ths2.append(t)
# TEXTFIX: strip compilation jargon from notes
import re as _re
for i in insts.values():
    i['note']=_re.sub(r';?\s*those cathedral and monastic schools are Region \d records\.?','. Those cathedral and monastic schools appear as separate entries.',i['note'])
    i['note']=_re.sub(r'Ownership: Gdańsk belonged to the Polish Crown \(Royal Prussia\) until 1793, hence placed in Region 6\. ','Gdańsk belonged to the Polish Crown (Royal Prussia) until 1793. ',i['note'])
out = {'inst': sorted(insts.values(), key=lambda i: i['s']), 'ev': evs, 'th': ths2,
       'labels': bm['labels']}
json.dump(out, open('/home/claude/build/data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('institutions', len(insts), 'events', len(evs), 'thinkers', len(ths2))
print('by inst type', collections.Counter(i['t'] for i in insts.values()))
print('by event type', collections.Counter(e['t'] for e in evs))
print(len(problems), 'problems'); print('\n'.join(problems[:80]))
