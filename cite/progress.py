import json, glob, collections, os
print('CITATIONS (unverified / total events, residencies)')
for f in sorted(glob.glob('/home/claude/cite/cites_*.json')):
    c = json.load(open(f)); g = os.path.basename(f)[6:-5]
    ev = collections.Counter(r.get('status') for r in c['events'].values())
    th = collections.Counter(r.get('status') for r in c['thinkers'].values())
    print(f"  {g:5} events {ev['unverified']:4}/{sum(ev.values()):4}  residencies {th['unverified']:4}/{sum(th.values()):4}")
print('PEOPLE (roster people with a record / roster size)')
for e in 'abcdef':
    roster = {r['id'] for r in json.load(open(f'/home/claude/cite/roster_{e}.json'))}
    try: have = {p['id'] for p in json.load(open(f'/home/claude/cite/people_{e}.json'))['people'] if p.get('stops')}
    except Exception: have = set()
    print(f"  era {e}: {len(roster & have):4}/{len(roster):4}")
