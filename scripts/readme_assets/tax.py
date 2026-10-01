import json
exec(open(__file__.replace('tax.py','flow.py'),encoding='utf-8').read().split('def flow')[0])
d=json.load(open('data/incidents.json',encoding='utf-8')); inc=d['incidents'] if isinstance(d,dict) else d
e=[x for x in inc if x['id']=='INC-00924'][0]
def codes(lst,n):
    lst=list(lst); return ' · '.join(lst[:n])+(f'   +{len(lst)-n} more' if len(lst)>n else '')
atl=e['mitre_atlas']; pri=['AML.T0051.001','AML.T0057','AML.T0024']; atl_s=pri+[a for a in atl if a not in pri]
nist=e['nist_ai_rmf']; npri=['MEASURE-2.7','MAP-3.5','MANAGE-2.3']; nist_s=npri+[a for a in nist if a not in npri]
mae=' · '.join(f"{m['layer']} {m['label']} ({m['role']})" for m in e['maestro_layers'])
T=[('OWASP LLM Top 10 (2026)','core',codes(e['owasp_llm'],6)),
   ('OWASP Agentic Top 10 (ASI)','core',codes(e['owasp_asi'],7)),
   ('NIST AI RMF (AI 100-1)','core',codes(nist_s,3)),
   ('MITRE ATLAS','core',codes(atl_s,3)),
   ('MAESTRO layers','companion',mae),
   ('VERIS 1.4.1 crosswalk','experimental','action:hacking:variety=Prompt injection')]
def tax(dark):
    c=pal(dark); W,H=1200,540; o=[]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{c["bg"]}" stroke="{c["bd"]}"/>')
    o.append(f'<text x="40" y="50" font-size="12" font-weight="700" letter-spacing="2" fill="{c["acc"]}">ONE ENTRY, SIX TAXONOMIES</text>')
    o.append(f'<text x="40" y="72" font-size="13" fill="{c["sub"]}">A real record as published in v2.10.0. Most labels in the corpus are heuristic-assigned; see the datasheet.</text>')
    # center
    cx,cy,cw,ch=430,185,340,220
    for i,(x,y) in enumerate([(40,100),(40,250),(40,400),(820,100),(820,250),(820,400)]):
        name,st,cd=T[i]; w,h=340,110
        dash={'core':'','companion':' stroke-dasharray="6 4"','experimental':' stroke-dasharray="2 4"'}[st]
        ax=x+w if x<600 else x; ay=y+h/2; bx=cx if x<600 else cx+cw
        by=cy+ch/2+(-40 if i%3==0 else 40 if i%3==2 else 0)
        o.append(f'<path d="M{ax} {ay} C {(ax+bx)/2} {ay}, {(ax+bx)/2} {by}, {bx} {by}" fill="none" stroke="{c["acc"]}" stroke-width="1.5" stroke-opacity="{0.9 if st=="core" else 0.5}"{dash}/>')
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{c["card"]}" stroke="{c["acc"] if st=="core" else c["line"]}" stroke-width="1.3"{dash}/>')
        o.append(f'<text x="{x+18}" y="{y+30}" font-size="15" font-weight="700" fill="{c["fg"]}">{name}</text>')
        bw=len(st)*7.2+18
        o.append(f'<rect x="{x+w-18-bw:.0f}" y="{y+15}" width="{bw:.0f}" height="22" rx="11" fill="{c["accbg"] if st=="core" else c["bg"]}" stroke="{c["acc"] if st=="core" else c["line"]}"/><text x="{x+w-18-bw/2:.0f}" y="{y+30}" text-anchor="middle" font-size="11.5" font-weight="650" fill="{c["acc"] if st=="core" else c["sub"]}">{st}</text>')
        # wrap codes over up to 2 lines
        words=cd.split(' · '); lines=['']
        for wd in words:
            t=(lines[-1]+' · '+wd) if lines[-1] else wd
            if len(t)*7.4>w-36 and lines[-1]: lines.append(wd)
            else: lines[-1]=t
        for k,l in enumerate(lines[:3]):
            o.append(f'<text x="{x+18}" y="{y+60+k*20}" font-size="13" font-family="ui-monospace,SFMono-Regular,Consolas,Menlo,monospace" fill="{c["fg"]}" fill-opacity="0.85">{l}</text>')
        if st=='experimental': o.append(f'<text x="{x+18}" y="{y+96}" font-size="11.5" fill="{c["sub"]}">emitted at export time from attack_vector</text>')
    o.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="{c["accbg"]}" stroke="{c["acc"]}" stroke-width="2"/>')
    o.append(f'<text x="{cx+22}" y="{cy+34}" font-size="13" font-weight="700" letter-spacing="1" font-family="ui-monospace,SFMono-Regular,Consolas,Menlo,monospace" fill="{c["acc"]}">INC-00924</text>')
    o.append(f'<text x="{cx+22}" y="{cy+66}" font-size="21" font-weight="800" fill="{c["fg"]}">EchoLeak</text>')
    o.append(f'<text x="{cx+22}" y="{cy+90}" font-size="13" fill="{c["sub"]}">Zero-click Microsoft Copilot data</text>')
    o.append(f'<text x="{cx+22}" y="{cy+108}" font-size="13" fill="{c["sub"]}">exfiltration via email prompt injection</text>')
    chips=[e['severity'],e['attack_vector'],e['cve_ids'][0],e['quality_tier']]
    x=cx+22; yy=cy+132
    for t in chips:
        w=len(t)*7.3+20
        if x+w>cx+cw-14: x=cx+22; yy+=34
        o.append(f'<rect x="{x:.0f}" y="{yy}" width="{w:.0f}" height="26" rx="13" fill="{c["bg"]}" stroke="{c["bd"]}"/><text x="{x+w/2:.0f}" y="{yy+17}" text-anchor="middle" font-size="12" font-weight="600" fill="{c["fg"]}">{t}</text>')
        x+=w+8
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Taxonomy map: incident INC-00924 (EchoLeak) mapped onto OWASP LLM Top 10 2026, OWASP Agentic Top 10, NIST AI RMF, MITRE ATLAS (core), MAESTRO (companion) and a VERIS crosswalk (experimental)" {F}>'+''.join(o)+'</svg>\n'
for n,dk in [('taxonomy-map-dark.svg',True),('taxonomy-map-light.svg',False)]:
    open('docs/assets/readme/'+n,'w',encoding='utf-8',newline='\n').write(tax(dk))
