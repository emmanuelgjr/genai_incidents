"""D155 counterfactual, step 1. Run INSIDE a scratch clone at the base commit: python cf_apply.py
Rewrites ingest/aiid_full.json for the title-reproducible candidates using the FIXED rules; then run
parse_existing.py + GENAI_REFRESH_RUN=1 merge_and_dedupe.py and diff with d155_counterfactual_diff.py (base build saved as ../base_incidents.json)."""
import json,re,sys
sys.path.insert(0,'scripts')
import scrape_aiid as new
rows=json.load(open('ingest/aiid_full.json',encoding='utf-8'))
EMB=re.compile('rce'); REAL=re.compile(r'\brce\b|remote code|command injection|sandbox escape')
# old-rule reference: new rules but with the old patterns
OLD_RULE=r"rce|remote code|command injection|sandbox escape"
def old_tx(e):
    t=(e['title']+' '+e['description']).lower()
    llm,asi,atl=set(),set(),set(); av='other'
    for p,l,a,m,v in new.TAXONOMY_RULES:
        if p.startswith(r'\brce'): p=OLD_RULE
        if re.search(p,t): llm.update(l);asi.update(a);atl.update(m)
        if re.search(p,t) and av=='other' and v!='other': av=v
    return sorted(llm),sorted(asi),sorted(atl),av
def old_sev(e):
    t=e['title'].lower()
    if any(k in t for k in ["killed","dead","fatal","death","ransom","$1m","millions","billion"]): return 'Critical'
    if any(k in t for k in ["breach","stolen","leaked","rce","remote code","exfiltrat"]): return 'High'
    return 'Medium'
cand=[];nonrep=[];changed=[]
for r in rows:
    t=r['title'].lower()
    if not (EMB.search(t) and not REAL.search(t)): continue
    e={'title':r['title'],'description':''}
    o=old_tx(e)
    stored=(r['owasp_llm'],r['owasp_asi'],r['mitre_atlas'],r['attack_vector'])
    if o!=stored or old_sev(e)!=r['severity']:
        nonrep.append(r['source_id']); continue
    cand.append(r['source_id'])
    tx=new.map_taxonomy(e)
    r['owasp_llm'],r['owasp_asi'],r['mitre_atlas'],r['attack_vector']=tx['owasp_llm'],tx['owasp_asi'],tx['mitre_atlas'],tx['attack_vector']
    r['severity']=new.severity_for(e)
json.dump(rows,open('ingest/aiid_full.json','w',encoding='utf-8'),indent=2,ensure_ascii=False)
print(len(cand),'reproducible',cand);print(len(nonrep),'not reproducible',nonrep)
