"""D155 counterfactual, step 2: per-entity diff of base vs counterfactual data/incidents.json (run in the scratch clone)."""
import json,collections
b={e['id']:e for e in json.load(open('../base_incidents.json',encoding='utf-8'))['incidents']}
n={e['id']:e for e in json.load(open('data/incidents.json',encoding='utf-8'))['incidents']}
print('ids same',set(b)==set(n),len(b),len(n))
f=collections.defaultdict(list)
for i in b:
    for k in set(b[i])|set(n.get(i,{})):
        if b[i].get(k)!=n[i].get(k): f[k].append(i)
for k,v in sorted(f.items()): print(k,len(v),' '.join(x.replace('INC-','') for x in v))
rows=set(sum(f.values(),[])); print('rows changed',len(rows))
print('attack_vector transitions',collections.Counter((b[i]['attack_vector'],n[i]['attack_vector']) for i in f['attack_vector']))
print('severity',collections.Counter((b[i]['severity'],n[i]['severity']) for i in f['severity']))
import sys
if len(sys.argv)>1:
  for i in sorted(rows):
    print(i,{k:(b[i].get(k),n[i].get(k)) for k in f if i in f[k] and k not in('updated','last_seen')})
