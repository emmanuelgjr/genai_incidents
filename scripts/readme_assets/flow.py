def pal(dark):
    return dict(bg='#0d1117' if dark else '#ffffff', card='#161b22' if dark else '#fafaf9', bd='#30363d' if dark else '#e7e5e4',
        fg='#e6edf3' if dark else '#1c1917', sub='#8b949e' if dark else '#78716c', acc='#f97316' if dark else '#c2410c',
        accbg='#2a1a10' if dark else '#fff1e6', line='#6e7681' if dark else '#a8a29e')
F='font-family="Inter,Segoe UI,system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif"'
def flow(dark):
    c=pal(dark); W,H=1200,500; o=[]
    def box(x,y,w,h,t,s=None,hi=False):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{c["accbg"] if hi else c["card"]}" stroke="{c["acc"] if hi else c["bd"]}" stroke-width="{1.5 if hi else 1}"/>')
        ty=y+h/2+(-3 if s else 5)
        o.append(f'<text x="{x+16}" y="{ty:.0f}" font-size="14.5" font-weight="650" fill="{c["fg"]}">{t}</text>')
        if s: o.append(f'<text x="{x+16}" y="{ty+18:.0f}" font-size="12" fill="{c["sub"]}">{s}</text>')
    def head(x,t,n):
        o.append(f'<text x="{x}" y="52" font-size="12" font-weight="700" letter-spacing="2" fill="{c["acc"]}">{n}</text><text x="{x+22}" y="52" font-size="12" font-weight="700" letter-spacing="2" fill="{c["sub"]}">{t}</text>')
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{c["bg"]}" stroke="{c["bd"]}"/>')
    head(40,'COLLECT','01'); head(452,'NORMALIZE','02'); head(866,'SHIP','03')
    src=[('AI Incident Database','official weekly snapshot'),('OECD AI Incidents Monitor',None),('AIAAIC Repository',None),('MITRE ATLAS','case studies'),('NVD · GHSA · OSV · CISA KEV','AI/ML CVEs'),('AVID · garak · promptfoo',None),('Researcher &amp; vendor reports','blogs, threat reports, papers')]
    y=72; sy=[]
    for t,s in src:
        h=52 if s else 42; box(40,y,290,h,t,s); sy.append(y+h/2); y+=h+8
    steps=[('Ingest','per-source parsers, polite conduct'),('Normalize','one schema for every source'),('Merge &amp; dedupe','CVE · source ID · URL · title'),('Map taxonomies','OWASP LLM · ASI · NIST · ATLAS'),('Validate','JSON Schema + CI drift gates')]
    y=80; py=[]
    for i,(t,s) in enumerate(steps):
        box(452,y,296,56,t,s,hi=(i==3)); py.append(y); 
        if i<len(steps)-1: o.append(f'<path d="M600 {y+56} v14" stroke="{c["acc"]}" stroke-width="2" marker-end="url(#a)"/>')
        y+=74
    o.append(f'<text x="600" y="{y+6}" text-anchor="middle" font-size="12" fill="{c["sub"]}">deterministic build · no model calls</text>')
    o.append(f'<text x="600" y="{y+24}" text-anchor="middle" font-size="12" fill="{c["sub"]}">stable IDs · tombstones, never deletions</text>')
    outs=[('Searchable website','filter · search · deep-link'),('JSON + JSON Schema','data/incidents.json'),('PyPI package','pip install genai-incidents'),('Hugging Face dataset','load_dataset(…)'),('STIX 2.1 · TAXII 2.1','x-genai-incident SDOs'),('MISP feed','ATLAS + VERIS tags')]
    y=72; oy=[]
    for t,s in outs:
        box(866,y,294,52,t,s); oy.append(y+26); y+=60
    mid=py[0]+28; midb=py[-1]+28
    for v in sy: o.append(f'<path d="M330 {v:.0f} C 395 {v:.0f}, 395 {(py[0]+28):.0f}, 448 {(py[0]+28):.0f}" fill="none" stroke="{c["line"]}" stroke-width="1.3" stroke-opacity="0.8"/>')
    for v in oy: o.append(f'<path d="M748 {midb} C 810 {midb}, 805 {v}, 862 {v}" fill="none" stroke="{c["line"]}" stroke-width="1.3" stroke-opacity="0.8"/>')
    o.append(f'<circle cx="448" cy="{py[0]+28}" r="4" fill="{c["acc"]}"/><circle cx="752" cy="{midb}" r="4" fill="{c["acc"]}"/>')
    defs=f'<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{c["acc"]}"/></marker></defs>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="How it works: public sources are collected, normalized onto one schema, deduplicated, mapped to OWASP, NIST and MITRE ATLAS taxonomies, validated, then shipped as a website, JSON, PyPI, Hugging Face, STIX/TAXII and MISP" {F}>{defs}'+''.join(o)+'</svg>\n'
for n,d in [('how-it-works-dark.svg',True),('how-it-works-light.svg',False)]:
    open('docs/assets/readme/'+n,'w',encoding='utf-8',newline='\n').write(flow(d))
