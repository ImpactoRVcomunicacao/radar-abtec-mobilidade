#!/usr/bin/env python3
import json,re
from pathlib import Path
try:
    from googlenewsdecoder import gnewsdecoder
except Exception:
    gnewsdecoder=None
BASE=Path('/opt/data/abtec_mobilidade_inteligencia')
data=json.loads((BASE/'buscas/google_news_teste_2026-09-17.json').read_text(encoding='utf-8'))
# manual curation from first test: choose high-signal items across ABtec and associates
need=[
 'ABtec Mobilidade nasce para dar voz',
 'ABTEC chega para fortalecer',
 'ABTEC defende tecnologia e governança',
 'Após Estudo Nacional de Mobilidade Urbana',
 'Prodata Mais Mobi leva tecnologia brasileira',
 'Prodata Mobility apresenta soluções de bilhetagem',
 'Transdata lança Pix por Aproximação',
 'Tecnologia e integração de sistemas redefinem',
 'Maringá e região metropolitana passam a aceitar pagamento por aproximação',
 'Empresa 1 leva soluções de digitalização',
 'IA transforma gestão do transporte público',
 'CittaMobi lança comunicado',
 'IPT disponibiliza parecer técnico sobre aplicativo Cittamobi',
 'Sonda apresenta tecnologias para transformar transporte',
 'Fortaleza transforma aplicativo de ônibus',
]
selected=[]
for needle in need:
    for it in data['items']:
        if needle.lower() in it.get('title','').lower():
            selected.append(it); break
seen=set(); out=[]
for it in selected:
    if it['title'] in seen: continue
    seen.add(it['title'])
    url=it['link']
    if gnewsdecoder and 'news.google.com' in url:
        try:
            r=gnewsdecoder(url, interval=.2)
            if r.get('status') and r.get('decoded_url'): url=r['decoded_url']
        except Exception: pass
    it=dict(it); it['url_original']=url; out.append(it)
(BASE/'buscas/selecionados_teste_2026-09-17.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('selected',len(out))
for it in out:
    print('-',it['bucket'], '|', it['source'], '|', it['title'])
    print(' ',it['url_original'])
