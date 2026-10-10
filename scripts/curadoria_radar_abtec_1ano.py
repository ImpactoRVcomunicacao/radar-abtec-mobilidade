#!/usr/bin/env python3
from pathlib import Path
import json,re,html,urllib.request,ssl
from datetime import date
try:
    from googlenewsdecoder import gnewsdecoder
except Exception:
    gnewsdecoder=None
ROOT=Path('/opt/data/abtec_mobilidade_inteligencia')
DATE='2026-10-10'
CUTOFF='2025-10-10'
raw=json.loads((ROOT/'buscas'/f'coleta_radar_abtec_{DATE}.json').read_text('utf-8'))
HEAD={'User-Agent':'Mozilla/5.0 Radar ABtec QA'}

def decode(url):
    if 'news.google.com' not in url or not gnewsdecoder: return url
    try:
        r=gnewsdecoder(url, interval=.15)
        if r.get('status') and r.get('decoded_url'): return r['decoded_url']
    except Exception: pass
    return url

def verify(url,title):
    try:
        ctx=ssl._create_unverified_context()
        r=urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=25,context=ctx)
        data=r.read(250000).decode('utf-8','ignore')
        m=re.search(r'<title[^>]*>([\s\S]*?)</title>',data,re.I)
        page=html.unescape(re.sub(r'\s+',' ',re.sub('<.*?>',' ',m.group(1))).strip()) if m else ''
        toks=[t.lower() for t in re.findall(r'[A-Za-zÁÉÍÓÚáéíóúÃÕãõÇç0-9]{5,}',title)[:8]]
        hay=(page+' '+data[:120000]).lower()
        return {'status':'ok' if r.status<400 and sum(t in hay for t in toks)>=1 else 'warn','code':r.status,'final_url':r.geturl(),'page_title':page}
    except Exception as e: return {'status':'error','error':str(e)[:180],'final_url':url,'page_title':''}
manual_keep=[
 ('ABtec Mobilidade','Governança de dados e transparência','ABTEC defende tecnologia e governança de dados como pilares para ampliar a transparência do transporte público'),
 ('ABtec Mobilidade','Transparência e ENMU','Após Estudo Nacional de Mobilidade Urbana apontar falhas na transparência, ABTEC defende uso de tecnologia para qualificar transporte público'),
 ('ABtec Mobilidade','Institucional / representação setorial','ABtec Mobilidade nasce para dar voz às desenvolvedoras de tecnologias e acelerar o amadurecimento do mercado'),
 ('ABtec Mobilidade','Institucional / tecnologia brasileira','ABTEC chega para fortalecer a tecnologia brasileira aplicada à mobilidade'),
 ('Bus2','Dados em tempo real / internacionalização','Aplicativo BuzzPY com tecnologia da brasileira Bus2 estreia no Paraguai com monitoramento em tempo real de ônibus'),
 ('Bus2','Apps de mobilidade','Lançado o primeiro app de mobilidade do Paraguai com tecnologia Bus2'),
 ('Bus2','Bilhetagem / dados urbanos','Da bilhetagem ao big data: Bus2 leva leitura inteligente dos ônibus brasileiros à Arena ANTP 2025'),
 ('Cittati','Smart cities e mobilidade urbana','IPT disponibiliza parecer técnico sobre aplicativo Cittamobi como solução tecnológica para Cidades Inteligentes em Mobilidade Urbana'),
 ('Cittati','App ao usuário / informação em tempo real','Novo aplicativo de transporte coletivo de Uberlândia Cittamobi já está em funcionamento'),
 ('Cittati','Plataforma passageiro-operador-gestor','Cittamobi: mais que um app, uma plataforma que une passageiro, operador e gestor do transporte'),
 ('Empresa 1','Bilhetagem digital / Lat.Bus','Empresa 1 leva à LAT.BUS 2026 soluções para digitalização da bilhetagem e gestão do transporte coletivo'),
 ('Empresa 1','Segurança / tecnologia embarcada','Empresa 1 usa tecnologia no transporte coletivo para reforçar segurança'),
 ('Empresa 1','PIX / validador','Florianópolis adota pagamento por Pix no validador dos ônibus'),
 ('Prodata Mobility Brasil','Internacionalização / eventos','Prodata Mais Mobi leva tecnologia brasileira ao maior evento de transporte público dos EUA'),
 ('Prodata Mobility Brasil','Bilhetagem como sensor urbano','“Bilhetagem é a maior rede de sensores de uma cidade”, diz Diretor Executivo Prodata Mais Mobi ao defender uso de dados na mobilidade'),
 ('Prodata Mobility Brasil','IA / gestão da mobilidade','Prodata Mais Mobi apresentará aplicações de inteligência artificial para gestão da mobilidade na Rio Innovation Week 2026'),
 ('Prodata Mobility Brasil','Pagamento digital / integração modal','Prodata Mobility Brasil inova mais uma vez e oferece experiência integrada nos modais de pagamento digital de ônibus e VLTs na Baixada Santista'),
 ('Prodata Mobility Brasil','Smart cities / mobilidade','Mais.Mobi estreia no Smart City Expo Curitiba 2026 com soluções inovadoras de mobilidade'),
 ('SONDA','Mobilidade inteligente / app','Fortaleza transforma aplicativo de ônibus em plataforma de mobilidade inteligente'),
 ('SONDA','Tecnologia / Lat.Bus','Sonda apresenta tecnologias para transformar transporte e mobilidade urbana durante a Lat.Bus2026'),
 ('Transdata','Integração de sistemas','Tecnologia e integração de sistemas redefinem o futuro do transporte público, aponta Romano Garcia, da Transdata'),
 ('Transdata','Carteira digital / open payment','Parceria entre Transdata, Prefeitura e VCG leva Carteira Google aos ônibus de Ponta Grossa'),
]
allitems=[]
for key in ['news_results','sector_results']:
    allitems += raw.get(key,[])
# exact/title contains matching
selected=[]; seen=set()
for emp,tema,want in manual_keep:
    want_norm=re.sub(r'\W+',' ',want.lower()).strip()
    best=None
    for it in allitems:
        title=it.get('title','')
        norm=re.sub(r'\W+',' ',title.lower()).strip()
        if want_norm[:65] in norm or norm[:65] in want_norm or len(set(want_norm.split()) & set(norm.split()))>=7:
            if emp==it.get('empresa') or emp in ['ABtec Mobilidade'] or it.get('empresa')==emp:
                best=it; break
    if not best:
        # try any company loosened
        for it in allitems:
            norm=re.sub(r'\W+',' ',it.get('title','').lower()).strip()
            if len(set(want_norm.split()) & set(norm.split()))>=7:
                best=it; break
    if best:
        url=decode(best.get('url',''))
        key=(emp,want,url)
        if key in seen: continue
        seen.add(key)
        selected.append({'empresa':emp,'tema':tema,'titulo':want,'resumo':'','impacto':'','url':url,'fonte':best.get('source') or best.get('portal') or '', 'data':best.get('date',''), 'id':f'achado-{len(selected)+1:02d}'})
# add official social/site block separately
social=raw.get('social_candidates',[])
# fill summaries/impacts manually by theme
summary_map={
 'Governança de dados e transparência':('A ABtec sustenta tecnologia e governança de dados como pilares para ampliar transparência no transporte público.','Base para pasta institucional sobre dados, accountability, qualidade de informação pública e maturidade digital dos sistemas.'),
 'Transparência e ENMU':('A cobertura conecta falhas apontadas no ENMU à necessidade de tecnologia para qualificar gestão e controle do transporte.','Reforça oportunidade de a ABtec liderar agenda de padrões, interoperabilidade e transparência para gestores.'),
 'Institucional / representação setorial':('A criação/posicionamento da ABtec aparece como resposta à necessidade de voz organizada das empresas de tecnologia de mobilidade.','Mostra espaço para construção de agenda setorial própria, separada de operadores e fabricantes.'),
 'Institucional / tecnologia brasileira':('A ABtec é apresentada como iniciativa para fortalecer tecnologia brasileira aplicada à mobilidade.','Ajuda a organizar narrativa de indústria nacional, inovação e soberania tecnológica.'),
 'Dados em tempo real / internacionalização':('Tecnologia da Bus2 aparece em app paraguaio com monitoramento em tempo real de ônibus.','Sinal de exportação de solução brasileira e valorização de informação ao passageiro como infraestrutura de confiança.'),
 'Apps de mobilidade':('O app paraguaio reforça presença de solução brasileira em operação fora do Brasil.','Útil para pasta de internacionalização e casos de replicabilidade regional.'),
 'Bilhetagem / dados urbanos':('A leitura inteligente da bilhetagem aparece conectada a big data e operação de ônibus.','Mostra tendência de bilhetagem deixar de ser só cobrança e virar sensor urbano de mobilidade.'),
 'Smart cities e mobilidade urbana':('Parecer técnico sobre CittaMobi aproxima app de mobilidade da agenda de cidades inteligentes.','Validação técnica externa fortalece a pasta Smart Cities da ABtec.'),
 'App ao usuário / informação em tempo real':('Uberlândia colocou o Cittamobi em operação como app do transporte coletivo.','Mostra demanda municipal por informação ao usuário, planejamento de viagens e relacionamento digital.'),
 'Plataforma passageiro-operador-gestor':('Cittamobi é descrito como plataforma que une passageiro, operador e gestor.','Indica mudança de apps isolados para ecossistemas de dados e gestão.'),
 'Bilhetagem digital / Lat.Bus':('Empresa 1 levou soluções de digitalização da bilhetagem e gestão à Lat.Bus 2026.','Feiras setoriais mostram portfólio e posicionamento competitivo das associadas.'),
 'Segurança / tecnologia embarcada':('Empresa 1 aparece em pauta sobre uso de tecnologia para reforçar segurança no transporte coletivo.','Segurança operacional e embarcada tende a crescer como argumento de valor para tecnologia.'),
 'PIX / validador':('Florianópolis adotou pagamento por Pix diretamente no validador dos ônibus.','PIX no validador reforça open payment brasileiro e inclusão de meios de pagamento populares.'),
 'Internacionalização / eventos':('Prodata/Mais Mobi levou tecnologia brasileira a evento internacional de transporte público.','Sinaliza vitrine global e pauta de exportação de tecnologia nacional.'),
 'Bilhetagem como sensor urbano':('Executivo da Prodata defende bilhetagem como grande rede de sensores da cidade.','É uma das teses mais fortes para tendência: dado transacional como inteligência urbana.'),
 'IA / gestão da mobilidade':('Prodata/Mais Mobi anunciou aplicações de IA para gestão da mobilidade.','Mostra IA entrando em produto e gestão, exigindo curadoria para separar caso concreto de hype.'),
 'Pagamento digital / integração modal':('Prodata aparece em experiência integrada de pagamento digital entre ônibus e VLTs na Baixada Santista.','Interoperabilidade modal e pagamento integrado são eixos centrais para smart mobility.'),
 'Smart cities / mobilidade':('Mais.Mobi aparece no Smart City Expo Curitiba com soluções de mobilidade.','A presença em eventos de cidades inteligentes ajuda a conectar mobilidade, dados e gestão urbana.'),
 'Mobilidade inteligente / app':('Fortaleza transformou app de ônibus em plataforma de mobilidade inteligente com SONDA.','Indica evolução de app informativo para plataforma urbana de serviços e dados.'),
 'Tecnologia / Lat.Bus':('SONDA apresentou tecnologias para transporte e mobilidade urbana na Lat.Bus 2026.','Sinal de posicionamento de TI corporativa dentro da agenda de transporte público.'),
 'Integração de sistemas':('Transdata destaca tecnologia e integração de sistemas como vetores do futuro do transporte público.','Integração sistêmica é condição para bilhetagem aberta, dados confiáveis e gestão multimodal.'),
 'Carteira digital / open payment':('Transdata aparece em parceria que leva Carteira Google aos ônibus de Ponta Grossa.','Carteiras digitais e aproximação reforçam a tendência de open payment no transporte.'),
}
for it in selected:
    it['resumo'], it['impacto']=summary_map.get(it['tema'],('Achado curado dentro da janela de um ano.','Relevante para monitoramento semanal da ABtec.'))
# verify only non-google links
qa=[]
for it in selected:
    qa.append({**verify(it['url'],it['titulo']),'id':it['id'],'titulo':it['titulo'],'url':it['url']})
# keep warnings but exclude errors
ok_ids={q['id'] for q in qa if q['status']!='error' and 'news.google.com' not in q['final_url']}
selected=[it for it in selected if it['id'] in ok_ids]
# rebuild ids after filtering
for i,it in enumerate(selected,1): it['id']=f'achado-{i:02d}'
outdir=ROOT/'edicoes-semanais'/DATE
outdir.mkdir(parents=True,exist_ok=True)
(outdir/'selecionados_curados.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
(outdir/'qa_links_curadoria.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'buscas'/f'sociais_associadas_{DATE}.json').write_text(json.dumps(social,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':len(selected),'qa_non_ok':[q for q in qa if q['status']=='error'][:5],'social':len(social)},ensure_ascii=False,indent=2))
for it in selected: print(it['id'],it['empresa'],it['tema'],it['url'])
