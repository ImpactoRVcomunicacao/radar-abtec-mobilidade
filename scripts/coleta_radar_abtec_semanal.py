#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, html, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'buscas'
FONTES=ROOT/'fontes'/'associadas_abtec_oficial.csv'
DATE=datetime.now(timezone.utc).date().isoformat()
HEAD={'User-Agent':'Mozilla/5.0 (Radar ABtec Mobilidade; contato ImpactoRVComunicacao)'}
KEYWORDS=[
 'smart city','smart cities','cidade inteligente','cidades inteligentes','mobilidade inteligente','bilhetagem','pagamento digital','ITS','AVL','SAE','MaaS','mobilidade urbana','transporte público','ônibus','BRT','metrô','trem','dados','inteligência artificial','IA','app','aplicativo','frota','validador','cartão transporte','monitoramento','GPS','centro de controle','CCO','PIX','open payment'
]
SOCIAL_DOMAINS=['linkedin.com','instagram.com','facebook.com','youtube.com','x.com','twitter.com']
SECTOR_SITES=['diariodotransporte.com.br','viatrolebus.com.br','technibus.com.br','mobilize.org.br','antp.org.br','antptrilhos.org.br','ntu.org.br','smartcitybusiness.com.br','connectedsmartcities.com.br','portal.connectedsmartcities.com.br','itdpbrasil.org','wri.org','bndes.gov.br','gov.br','prefeitura.sp.gov.br']


def fetch(url, timeout=25):
    try:
        req=urllib.request.Request(url,headers=HEAD)
        with urllib.request.urlopen(req,timeout=timeout) as r:
            ct=r.headers.get('content-type','')
            data=r.read(700000)
            text=data.decode('utf-8','ignore')
            return {'ok':True,'status':r.status,'url':r.geturl(),'content_type':ct,'text':text}
    except Exception as e:
        return {'ok':False,'status':None,'url':url,'error':str(e)[:250],'text':''}

def textify(s):
    s=re.sub(r'<script[\s\S]*?</script>',' ',s,flags=re.I)
    s=re.sub(r'<style[\s\S]*?</style>',' ',s,flags=re.I)
    s=html.unescape(re.sub(r'<[^>]+>',' ',s))
    return re.sub(r'\s+',' ',s).strip()

def page_title(s):
    m=re.search(r'<title[^>]*>([\s\S]*?)</title>',s,re.I)
    return textify(m.group(1)) if m else ''

def extract_links(base_url, text, limit=120):
    links=[]; seen=set()
    for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',text,re.I):
        href=urljoin(base_url, html.unescape(m.group(1).strip()))
        if href.startswith('mailto:') or href.startswith('tel:') or href.startswith('javascript:'): continue
        label=textify(m.group(2))[:220]
        key=href.split('#')[0]
        if key in seen: continue
        seen.add(key)
        links.append({'label':label,'url':key})
        if len(links)>=limit: break
    return links

def gnews(query, days_hint='7d'):
    url='https://news.google.com/rss/search?hl=pt-BR&gl=BR&ceid=BR:pt-419&q='+urllib.parse.quote(query)
    try:
        data=urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=25).read()
        root=ET.fromstring(data)
        items=[]
        for item in root.findall('.//item')[:15]:
            title=html.unescape(item.findtext('title','')).strip()
            link=item.findtext('link','').strip()
            source=item.find('source').text if item.find('source') is not None else ''
            pub=item.findtext('pubDate','')
            items.append({'title':title,'url':link,'source':source,'pubDate':pub,'query':query})
        return items
    except Exception as e:
        return [{'error':str(e)[:200],'query':query}]

def relevance(title, url, text=''):
    hay=(title+' '+url+' '+text[:5000]).lower()
    score=0
    matched=[]
    for k in KEYWORDS:
        if k.lower() in hay:
            score+=1; matched.append(k)
    if any(k in hay for k in ['abtec','prodata','transdata','cittati','cittamobi','onboard','empresa1','empresa 1','sonda','planeta informática','bus2','aequante']): score+=2
    if any(k in hay for k in ['evento','webinar','contrato','parceria','licitação','lançamento','implantação','prefeitura','governo','bilhetagem','pagamento','tecnologia','mobilidade']): score+=1
    if any(k in hay for k in ['vaga','trabalhe conosco','política de privacidade','cookies','login','2ª via','segunda via']): score-=2
    return score, matched[:8]

def load_companies():
    rows=[]
    with FONTES.open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

companies=load_companies()
site_results=[]; social_candidates=[]; news_results=[]; sector_results=[]

for c in companies:
    name=c['nome_oficial']; site=c.get('site','')
    if site:
        res=fetch(site)
        links=extract_links(res['url'] if res['ok'] else site, res['text']) if res['text'] else []
        title=page_title(res['text']) if res['text'] else ''
        body=textify(res['text'])[:4000] if res['text'] else ''
        score, matched=relevance(title, site, body)
        interesting=[]
        for l in links:
            s,m=relevance(l['label'],l['url'])
            if s>=1 or any(d in l['url'].lower() for d in SOCIAL_DOMAINS):
                interesting.append({**l,'score':s,'keywords':m})
            if any(d in l['url'].lower() for d in SOCIAL_DOMAINS):
                social_candidates.append({'empresa':name,'plataforma':urlparse(l['url']).netloc,'url':l['url'],'label':l['label'],'fonte':'site oficial'})
        site_results.append({'empresa':name,'site':site,'ok':res['ok'],'status':res['status'],'final_url':res.get('url'), 'title':title,'score':score,'keywords':matched,'links_relevantes':interesting[:25],'erro':res.get('error')})
    aliases=[a.strip() for a in c.get('aliases','').split(';') if a.strip()]
    queries=[]
    queries.append(f'"{name}" mobilidade transporte público tecnologia')
    for a in aliases[:3]: queries.append(f'"{a}" mobilidade transporte público')
    queries.append(f'"{name}" smart cities OR "cidade inteligente"')
    for q in queries:
        for it in gnews(q):
            if 'error' in it:
                news_results.append({'empresa':name,**it}); continue
            sc,kw=relevance(it['title'],it['url'])
            if sc>=1:
                news_results.append({'empresa':name,'score':sc,'keywords':kw,**it})

# sector portal cross-search by company names and general ABtec theme
for site in SECTOR_SITES:
    for c in companies:
        name=c['nome_oficial']
        q=f'site:{site} "{name}" OR "{name.split()[0]}" mobilidade transporte público tecnologia'
        for it in gnews(q):
            if 'error' in it: continue
            sc,kw=relevance(it['title'],it['url'])
            if sc>=1:
                sector_results.append({'empresa':name,'portal':site,'score':sc,'keywords':kw,**it})

# de-duplicate news by title/url
for arr_name in ['news_results','sector_results']:
    arr=locals()[arr_name]
    seen=set(); ded=[]
    for it in sorted(arr,key=lambda x:x.get('score',0), reverse=True):
        key=(re.sub(r'\W+',' ',it.get('title','').lower()).strip()[:120], it.get('url','')[:120])
        if key in seen: continue
        seen.add(key); ded.append(it)
    locals()[arr_name][:]=ded

out={'date':DATE,'companies':companies,'site_results':site_results,'social_candidates':social_candidates,'news_results':news_results,'sector_results':sector_results}
(OUT/f'coleta_radar_abtec_{DATE}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
# CSV resumo
with (OUT/f'achados_radar_abtec_{DATE}.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f); w.writerow(['tipo','empresa','score','fonte','titulo_label','url','keywords'])
    for s in site_results:
        w.writerow(['site',s['empresa'],s['score'],s['site'],s['title'],s['final_url'], '|'.join(s.get('keywords',[]))])
        for l in s.get('links_relevantes',[])[:8]:
            w.writerow(['site_link',s['empresa'],l['score'],s['site'],l['label'],l['url'],'|'.join(l.get('keywords',[]))])
    for n in news_results[:100]:
        w.writerow(['news',n.get('empresa'),n.get('score'),n.get('source'),n.get('title'),n.get('url'),'|'.join(n.get('keywords',[]))])
    for n in sector_results[:100]:
        w.writerow(['setorial',n.get('empresa'),n.get('score'),n.get('portal'),n.get('title'),n.get('url'),'|'.join(n.get('keywords',[]))])
    for s in social_candidates:
        w.writerow(['social',s['empresa'],'',s['plataforma'],s['label'],s['url'],''])
# Markdown triage
lines=[f'# Radar ABtec Mobilidade — coleta inicial {DATE}', '', '## Escopo', 'ABtec Mobilidade e associadas oficiais mapeadas em abtecbr.org.', '', '## Sites oficiais verificados']
for s in site_results:
    lines.append(f'- **{s["empresa"]}** — {"OK" if s["ok"] else "ERRO"} — {s.get("title") or s.get("erro") or s["site"]}')
lines += ['', '## Canais sociais encontrados nos sites oficiais']
for s in social_candidates[:80]: lines.append(f'- **{s["empresa"]}** — {s["plataforma"]}: {s["url"]}')
lines += ['', '## Achados em imprensa / Google News (triagem automática; revisar antes de publicar)']
for n in news_results[:40]: lines.append(f'- **{n.get("empresa")}** [{n.get("score")}] {n.get("title")} — {n.get("source")} — {n.get("url")}')
lines += ['', '## Achados em portais setoriais/tecnologia (triagem automática; revisar antes de publicar)']
for n in sector_results[:40]: lines.append(f'- **{n.get("empresa")}** [{n.get("score")}] {n.get("title")} — {n.get("portal")} — {n.get("url")}')
lines += ['', '## Próximo passo editorial', 'Abrir manualmente os achados com score alto, validar data/fonte, remover falsos positivos e transformar em tendências semanais.']
(OUT/f'resumo_coleta_radar_abtec_{DATE}.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'date':DATE,'companies':len(companies),'sites':len(site_results),'social_candidates':len(social_candidates),'news_results':len(news_results),'sector_results':len(sector_results),'json':str(OUT/f'coleta_radar_abtec_{DATE}.json'),'csv':str(OUT/f'achados_radar_abtec_{DATE}.csv'),'md':str(OUT/f'resumo_coleta_radar_abtec_{DATE}.md')},ensure_ascii=False,indent=2))
