#!/usr/bin/env python3
from __future__ import annotations
import json, re, html, urllib.request
from pathlib import Path
from datetime import datetime, timezone
try:
    from googlenewsdecoder import gnewsdecoder
except Exception:
    gnewsdecoder=None
ROOT=Path(__file__).resolve().parents[1]
DATE=datetime.now(timezone.utc).date().isoformat()
SRC=ROOT/'buscas'/f'coleta_radar_abtec_{DATE}.json'
OUTDIR=ROOT/'edicoes-semanais'/DATE
OUTDIR.mkdir(parents=True,exist_ok=True)
HEAD={'User-Agent':'Mozilla/5.0 Radar ABtec QA'}
KEY_ASSOC=['ABtec Mobilidade','Bus2','Cittati','Empresa 1','ONBOARD','Planeta Informática','Prodata Mobility Brasil','SONDA','Transdata']
THEMES=[
 ('Governança de dados e transparência',['ABTEC defende tecnologia','transparência','governança de dados']),
 ('Bilhetagem, pagamentos digitais e open payment',['bilhetagem','pagamento','QR Code','WhatsApp','Pix','aproximação','cartões']),
 ('IA, dados em tempo real e gestão operacional',['inteligência artificial','IA','dados em tempo real','monitoramento em tempo real','AVL','gestão da frota']),
 ('Apps ao usuário e experiência do passageiro',['aplicativo','app','CittaMobi','Bus2','previsão','chegada']),
 ('Smart cities e mobilidade urbana inteligente',['smart cities','Cidades Inteligentes','mobilidade inteligente','cidades inteligentes'])
]

def decode(url):
    if 'news.google.com' not in url or not gnewsdecoder: return url
    try:
        r=gnewsdecoder(url, interval=.15)
        if r.get('status') and r.get('decoded_url'): return r['decoded_url']
    except Exception: pass
    return url

def fetch_title(url):
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=20)
        data=r.read(250000).decode('utf-8','ignore')
        m=re.search(r'<title[^>]*>([\s\S]*?)</title>',data,re.I)
        t=html.unescape(re.sub(r'\s+',' ',re.sub('<.*?>',' ',m.group(1))).strip()) if m else ''
        return {'ok':True,'status':r.status,'final_url':r.geturl(),'title':t}
    except Exception as e:
        return {'ok':False,'error':str(e)[:160],'final_url':url,'title':''}

def clean_title(t):
    t=re.sub(r'\s+-\s+[^-]{2,80}$','',t).strip()
    return t

def classify(t):
    low=t.lower()
    out=[]
    for theme,ks in THEMES:
        if any(k.lower() in low for k in ks): out.append(theme)
    return out or ['Tecnologia aplicada à mobilidade']

data=json.loads(SRC.read_text(encoding='utf-8'))
items=[]; seen=set()
for block in ['news_results','sector_results']:
    for it in data.get(block,[]):
        if it.get('score',0)<5: continue
        emp=it.get('empresa','')
        title=clean_title(it.get('title',''))
        if not title: continue
        # remove obvious wrong associations from buggy sector cross-search: title must mention company, ABtec, or tech theme strongly
        low=title.lower()
        if emp and emp not in ['ABtec Mobilidade']:
            aliases=[]
            if emp=='Prodata Mobility Brasil': aliases=['prodata','mais mobi']
            elif emp=='Empresa 1': aliases=['empresa 1','bilhetagem digital']
            elif emp=='Cittati': aliases=['cittati','cittamobi']
            elif emp=='Bus2': aliases=['bus2','buzzpy']
            elif emp=='SONDA': aliases=['sonda']
            elif emp=='Transdata': aliases=['transdata']
            elif emp=='ONBOARD': aliases=['onboard']
            elif emp=='Planeta Informática': aliases=['planeta informática','planeta']
            if aliases and not any(a in low for a in aliases) and block=='sector_results':
                continue
        key=re.sub(r'\W+',' ',title.lower()).strip()[:140]
        if key in seen: continue
        seen.add(key)
        url=decode(it.get('url',''))
        qa=fetch_title(url)
        if not qa['ok']:
            continue
        items.append({
            'empresa':emp,'source':it.get('source') or it.get('portal') or '', 'score':it.get('score'), 'title':title,
            'url':qa['final_url'], 'page_title':qa['title'], 'themes':classify(title), 'keywords':it.get('keywords',[])
        })
items=items[:24]
# group theme summaries
trend_counts={}
for it in items:
    for th in it['themes']: trend_counts[th]=trend_counts.get(th,0)+1
# social rows from official sites
social=data.get('social_candidates',[])
# HTML style based on prototype but compact
css='''
:root{--navy:#10243f;--blue:#1167b1;--cyan:#1ab7c8;--green:#00a884;--amber:#f4a340;--red:#c43d32;--ink:#17212b;--muted:#667787;--line:#dbe7ef;--bg:#f5f8fb;--soft:#fbfdff}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);font-family:Inter,Arial,Helvetica,sans-serif;color:var(--ink);line-height:1.5}.wrap{max-width:1080px;margin:auto;background:#fff;min-height:100vh;padding:24px}.bar{height:10px;background:linear-gradient(90deg,var(--navy),var(--blue),var(--cyan));margin:-24px -24px 24px}.hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.title{font-size:32px;line-height:1;font-weight:950;color:var(--navy);text-transform:uppercase}.subtitle{margin-top:10px;color:var(--muted);font-size:15px}.date{margin-top:8px;font-weight:850}.logo{border:2px solid var(--blue);border-radius:16px;padding:10px 12px;background:#fff;color:var(--blue);font-weight:950;text-align:center}.intro,.summary,.section{border:1px solid var(--line);border-radius:18px;background:var(--soft);padding:16px;margin:16px 0}.jump{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.jump a{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#fff;color:var(--blue);text-decoration:none;font-weight:850}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:12px 0;break-inside:avoid}.badge{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:900;background:#e8f4ff;color:var(--blue);border:1px solid #b9d8f2}.meta{margin:8px 0;color:var(--muted);font-size:13px;font-weight:750}.card h3{margin:8px 0;color:var(--navy);font-size:18px;line-height:1.15}.btn{display:inline-block;margin-top:8px;border-radius:999px;background:var(--navy);color:#fff;text-decoration:none;font-weight:900;padding:9px 13px}.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{border-radius:999px;border:1px solid var(--line);background:#fff;padding:6px 10px;font-weight:800;font-size:13px}.foot{border-top:1px solid var(--line);margin-top:24px;padding-top:14px;color:var(--muted);font-size:13px}@media(max-width:720px){.hero{display:block}.title{font-size:27px}.wrap{padding:18px}.bar{margin:-18px -18px 20px}}
'''
parts=[f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade — coleta inicial {DATE}</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div><section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Smart cities, tecnologia aplicada à mobilidade e ecossistema brasileiro de bilhetagem/dados/ITS</div><div class="date">Coleta inicial — {DATE}</div></div><div class="logo">ABtec<br>Mobilidade</div></section>''']
parts.append(f'<section class="intro"><strong>Teste editorial:</strong> primeira varredura automatizada com triagem preliminar. Foram verificados {len(data.get("site_results",[]))} sites oficiais, {len(social)} canais sociais candidatos e {len(items)} achados de imprensa/setor selecionados para revisão humana.</section>')
parts.append('<nav class="jump"><a href="#tendencias">Tendências</a><a href="#associadas">Associadas</a><a href="#sociais">Canais sociais</a><a href="#achados">Achados</a></nav>')
parts.append('<section class="summary" id="tendencias"><h2>Tendências preliminares</h2><div class="grid">')
for th,n in sorted(trend_counts.items(),key=lambda x:x[1], reverse=True):
    parts.append(f'<article class="card"><span class="badge">Tendência</span><h3>{html.escape(th)}</h3><p>{n} achados associados nesta coleta. Tema deve ser acompanhado para relatório semanal e pastas temáticas da ABtec.</p></article>')
parts.append('</div></section>')
parts.append('<section class="section" id="associadas"><h2>Associadas oficiais monitoradas</h2><div class="chips">')
for c in data.get('companies',[]): parts.append(f'<span class="chip">{html.escape(c["nome_oficial"])}</span>')
parts.append('</div></section>')
parts.append('<section class="section" id="sociais"><h2>Canais sociais encontrados nos sites oficiais</h2><div class="grid">')
for s in social[:30]:
    parts.append(f'<article class="card"><span class="badge">Social oficial/candidato</span><h3>{html.escape(s["empresa"])}</h3><div class="meta">{html.escape(s["plataforma"])}</div><a class="btn" href="{html.escape(s["url"])}" target="_blank" rel="noopener">Abrir canal</a></article>')
parts.append('</div></section>')
parts.append('<section class="section" id="achados"><h2>Achados selecionados para revisão</h2>')
for it in items:
    parts.append(f'''<article class="card"><span class="badge">{html.escape(' · '.join(it['themes'][:2]))}</span><div class="meta">{html.escape(it['empresa'])} | {html.escape(it['source'])} | score {it['score']}</div><h3>{html.escape(it['title'])}</h3><p>Por que importa: sinal sobre tecnologia, dados, pagamento, operação ou experiência do passageiro no ecossistema de mobilidade urbana.</p><a class="btn" href="{html.escape(it['url'])}" target="_blank" rel="noopener">Abrir fonte original</a></article>''')
parts.append('</section>')
parts.append('<footer class="foot"><p><strong>Nota:</strong> esta é uma coleta inicial para validação do método. Antes de envio externo, os achados devem passar por curadoria editorial, verificação de data e remoção de falsos positivos.</p></footer></main></body></html>')
html_out=''.join(parts)
(OUTDIR/'index.html').write_text(html_out,encoding='utf-8')
(OUTDIR/'selecionados_preliminares.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
# update landing page links
idx=ROOT/'index.html'
if idx.exists():
    s=idx.read_text(encoding='utf-8')
    link=f'<p><a class="btn" href="/radar-abtec-mobilidade/edicoes-semanais/{DATE}/">Abrir coleta inicial com conteúdo — {DATE}</a></p>'
    if f'edicoes-semanais/{DATE}/' not in s:
        s=s.replace('</main>', link+'</main>') if '</main>' in s else s+link
        idx.write_text(s,encoding='utf-8')
print(json.dumps({'date':DATE,'selected':len(items),'out':str(OUTDIR/'index.html'),'json':str(OUTDIR/'selecionados_preliminares.json')},ensure_ascii=False,indent=2))
