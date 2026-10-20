#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, html, urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT=Path('/opt/data/abtec_mobilidade_inteligencia')
OUT=ROOT/'buscas'
RUN_DATE='2026-10-20'
WINDOW_START='2026-10-16'
HEAD={'User-Agent':'Mozilla/5.0 (Radar ABtec Mobilidade; research bot)'}
SOURCES={
  'ABtec Mobilidade — releases':'https://abtecbr.org/comunicacao/releases',
  'ABtec Mobilidade — notícias':'https://abtecbr.org/comunicacao/noticias',
  'Bus2 — blog':'https://bus2.blog/',
  'Cittati — blog':'https://www.cittati.com.br/blog',
  'Empresa 1 — transporte':'https://www.empresa1.com.br/categoria/transporte/',
  'ONBOARD — publicações':'https://onboard.com.br/blog',
  'Planeta Informática — notícias':'https://www.planeta.inf.br/noticias/',
  'Prodata Mobility Brasil':'https://www.prodatamobility.com.br/',
  'SONDA — notícias':'https://www.sonda.com/pt/quem-somos/noticias',
  'Transdata':'https://www.itstransdata.com/',
  'NTU':'https://www.ntu.org.br/',
  'Semove Rio':'https://semove.org.br/',
  'ABRATI':'https://www.abrati.org.br/',
  'FETPESP':'https://fetpesp.org.br/',
  'ANTP':'https://antp.org.br/',
  'ANPTrilhos':'https://anptrilhos.org.br/',
  'Diário do Transporte':'https://diariodotransporte.com.br/',
  'Technibus':'https://technibus.com.br/',
  'Via Trolebus':'https://viatrolebus.com.br/',
  'Mobilize':'https://www.mobilize.org.br/',
  'Frota&Cia':'https://frotacia.com.br/',
  'Connected Smart Cities':'https://connectedsmartcities.com.br/',
  'BNDES':'https://www.bndes.gov.br/wps/portal/site/home',
  'Ministério das Cidades':'https://www.gov.br/cidades/pt-br/assuntos/mobilidade-urbana',
  'WRI Brasil':'https://wricidades.org/',
  'ITDP Brasil':'https://itdpbrasil.org/'
}
TERMS=re.compile(r'\b(abtec|bus2|aequante|cittati|empresa\s?1|onboard|prodata|transdata|sonda|planeta|bilhetagem|pagamento|pix|emv|open payment|its|avl|sae|intelig[eê]ncia artificial|\bia\b|dados|smart cit|frota|mobilidade|transporte p[úu]blico|ônibus|brt|metr[oô]|integra[cç][aã]o|seguran[cç]a)\b',re.I)
EXCLUDE=re.compile(r'(sonda (?:nasog[aá]strica|de gastrostomia)|onboard(?:ing)?\s+(?:de |para )?(?:funcion[aá]rios|clientes|empresa)|vaga|trabalhe conosco|pol[ií]tica de privacidade)',re.I)

def fetch(url):
  try:
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=25) as r:
      raw=r.read(800000)
      return {'ok':True,'status':r.status,'final_url':r.geturl(),'text':raw.decode('utf-8','ignore'),'error':''}
  except Exception as e:
    return {'ok':False,'status':None,'final_url':url,'text':'','error':str(e)[:240]}

def clean(s):
  s=re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>',' ',s,flags=re.I)
  return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()

def title(s):
  m=re.search(r'<title[^>]*>(.*?)</title>',s,re.I|re.S)
  return clean(m.group(1))[:300] if m else ''

def links(base,text):
  seen=set(); out=[]
  for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',text,re.I|re.S):
    u=urljoin(base,html.unescape(m.group(1))).split('#')[0]
    if not u.startswith('http') or u in seen: continue
    seen.add(u); lab=clean(m.group(2))[:400]
    out.append({'title':lab,'url':u})
  return out

checked=[]; candidates=[]
for source,url in SOURCES.items():
  r=fetch(url); checked.append({'source':source,'url':url,'ok':r['ok'],'status':r['status'],'final_url':r['final_url'],'page_title':title(r['text']),'error':r['error']})
  if not r['ok']: continue
  for l in links(r['final_url'],r['text']):
    hay=f"{l['title']} {l['url']}"
    # Preserve strict increments via URL date. Pages with no date stay as source checks only.
    date_match=re.search(r'2026[/-]10[/-](?:16|17|18|19|20)',hay)
    if date_match and TERMS.search(hay) and not EXCLUDE.search(hay):
      candidates.append({'source':source,'title':l['title'],'url':l['url'],'date_hint':date_match.group(0)})

# hard-verified direct original items from the immediate preceding collection, retained as context only if within the incremental window.
context=[
 {'source':'Diário do Transporte','title':'ABtec Mobilidade leva indústria de tecnologia ao fórum do Ministério das Cidades sobre transporte público','url':'https://diariodotransporte.com.br/2026/10/15/abtec-mobilidade-leva-industria-de-tecnologia-ao-forum-do-ministerio-das-cidades-sobre-transporte-publico/','date':'2026-10-15','status':'já registrado — fora da janela'},
 {'source':'Diário do Transporte','title':'Prodata Mobility participa de missão comercial no Vietnã e avalia oportunidades em bilhetagem eletrônica','url':'https://diariodotransporte.com.br/2026/10/15/prodata-mobility-participa-de-missao-comercial-no-vietna-e-avalia-oportunidades-em-bilhetagem-eletronica/','date':'2026-10-15','status':'já registrado — fora da janela'},
 {'source':'Technibus','title':'ABtec Mobilidade participa do Fórum Consultivo de Mobilidade Urbana do Ministério das Cidades','url':'https://technibus.com.br/2026/10/15/abtec-mobilidade-participa-do-forum-consultivo-de-mobilidade-urbana-do-ministerio-das-cidades','date':'2026-10-15','status':'já registrado — fora da janela'}]
# dedupe and scope check
out=[]; seen=set()
for c in candidates:
  key=c['url']
  if key not in seen:
    seen.add(key); out.append(c)
result={'run_date':RUN_DATE,'window_start':WINDOW_START,'window_end':RUN_DATE,'sources_checked':checked,'new_candidates':out,'context_excluded':context,'notes':['Coleta incremental com fontes diretas; candidatos exigem validação de página individual antes de curadoria.','Não foram usados links do Google News como destino final.']}
OUT.mkdir(exist_ok=True)
json_path=OUT/f'incremental_radar_abtec_{RUN_DATE}.json'
csv_path=OUT/f'incremental_radar_abtec_{RUN_DATE}.csv'
md_path=OUT/f'resumo_incremental_radar_abtec_{RUN_DATE}.md'
json_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with csv_path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['tipo','fonte','titulo','url','status'])
  w.writeheader()
  for s in checked:w.writerow({'tipo':'fonte_verificada','fonte':s['source'],'titulo':s['page_title'],'url':s['final_url'],'status':f"{'OK' if s['ok'] else 'ERRO'} {s['status'] or ''}".strip()})
  for c in out:w.writerow({'tipo':'candidato_incremental','fonte':c['source'],'titulo':c['title'],'url':c['url'],'status':c['date_hint']})
lines=[f'# Radar ABtec Mobilidade — coleta incremental {RUN_DATE}','',f'Janela: {WINDOW_START} a {RUN_DATE}.','',f'## Fontes verificadas ({sum(s["ok"] for s in checked)}/{len(checked)} acessíveis)']
for s in checked: lines.append(f"- {'OK' if s['ok'] else 'ERRO'} — {s['source']} — {s['final_url']}")
lines+=['','## Candidatos incrementais']
if out:
  for c in out: lines.append(f"- {c['source']} — {c['title']} — {c['url']}")
else: lines.append('- Nenhum candidato novo com data na janela foi extraído das páginas iniciais/canais consultados.')
lines+=['','## Exclusões de continuidade']
for c in context: lines.append(f"- {c['date']} — {c['title']} — {c['status']}")
md_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'checked':len(checked),'accessible':sum(s['ok'] for s in checked),'new_candidates':len(out),'files':[str(json_path),str(csv_path),str(md_path)]},ensure_ascii=False))
