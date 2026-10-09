#!/usr/bin/env python3
import urllib.request, urllib.parse, xml.etree.ElementTree as ET, json, html, re
from pathlib import Path
DATE='2026-09-17'
queries={
 'ABtec Mobilidade':['"ABtec Mobilidade"','"ABTEC Mobilidade"','"Associação Brasileira de Tecnologia para a Mobilidade"'],
 'Prodata':['Prodata mobilidade bilhetagem transporte público','"Prodata" "bilhetagem" "transporte público"'],
 'Transdata':['Transdata mobilidade bilhetagem transporte público','"Transdata" "bilhetagem"'],
 'Onboard':['Onboard mobilidade transporte público bilhetagem','"Onboard" "mobilidade" "transporte público"'],
 'Empresa 1':['"Empresa 1" mobilidade transporte público bilhetagem','"Empresa1" transporte público'],
 'Cittati':['Cittati CittaMobi mobilidade transporte público','"CittaMobi" "transporte público"'],
 'SONDA':['SONDA mobilidade transporte público bilhetagem smart cities','"SONDA" "mobilidade" "transporte público"'],
 'Planeta Informática':['"Planeta Informática" mobilidade transporte público','"Planeta Informática" bilhetagem'],
 'Bus2 / Aequante':['Bus2 Aequante mobilidade transporte público','"Aequante" "Bus2"','"Bus2" "mobilidade"'],
 'Temas':['"smart cities" mobilidade Brasil transporte público tecnologia','"cidades inteligentes" mobilidade urbana tecnologia transporte público Brasil','IA mobilidade urbana transporte público Brasil bilhetagem']
}
HEAD={'User-Agent':'Mozilla/5.0 Radar ABtec test'}
def rss(q):
    url='https://news.google.com/rss/search?hl=pt-BR&gl=BR&ceid=BR:pt-419&q='+urllib.parse.quote(q)
    try:
        data=urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=25).read()
        root=ET.fromstring(data)
        out=[]
        for item in root.findall('.//item')[:8]:
            title=html.unescape(item.findtext('title','')).strip()
            link=item.findtext('link','').strip()
            source_el=item.find('source')
            source=source_el.text if source_el is not None and source_el.text else ''
            pub=item.findtext('pubDate','')
            out.append({'title':title,'link':link,'source':source,'pubDate':pub,'query':q})
        return out
    except Exception as e:
        return [{'error':repr(e),'query':q}]
items=[]
seen=set()
for bucket,qs in queries.items():
    for q in qs:
        for it in rss(q):
            if 'error' in it:
                items.append({'bucket':bucket,**it}); continue
            key=re.sub(r'\W+',' ',it['title'].lower()).strip()
            if key in seen: continue
            seen.add(key)
            items.append({'bucket':bucket,**it})
Path('/opt/data/abtec_mobilidade_inteligencia/buscas/google_news_teste_2026-09-17.json').write_text(json.dumps({'date':DATE,'items':items},ensure_ascii=False,indent=2),encoding='utf-8')
print('items',len(items))
for it in items[:80]:
    print('\n##',it.get('bucket'), '|', it.get('source'))
    print(it.get('title') or it.get('error'))
    print(it.get('link',''))
