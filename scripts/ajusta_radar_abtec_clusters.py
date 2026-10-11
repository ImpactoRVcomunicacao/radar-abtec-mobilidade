#!/usr/bin/env python3
from pathlib import Path
import json,csv,html,re
ROOT=Path('/opt/data/abtec_mobilidade_inteligencia')
DATE='2026-10-10'
SEL=ROOT/'edicoes-semanais'/DATE/'selecionados_curados.json'
items=json.loads(SEL.read_text('utf-8'))
# fix Prodata/Mais.Mobi summary if stale CittaMobi text leaked
for it in items:
    if it['titulo']=='Mais.Mobi estreia no Smart City Expo Curitiba 2026':
        it['resumo']='A Mais.Mobi apareceu no Smart City Expo Curitiba 2026 com soluções de mobilidade, reforçando presença em eventos de cidades inteligentes.'
        it['impacto']='Conecta tecnologia de mobilidade ao ecossistema de smart cities, útil para mapear vitrines e eventos estratégicos da ABtec Mobilidade.'
# add incremental validated item, if missing
new_url='https://diariodotransporte.com.br/2026/10/10/bilhete-unico-de-sao-paulo-e-citado-pela-uitp-entre-referencias-mundiais-de-bilhetagem-e-pix-aparece-entre-novas-alternativas-para-o-transporte-publico/'
if not any(it.get('url')==new_url for it in items):
    items.append({
        'empresa':'Ecossistema Smart Cities',
        'tema':'Bilhetagem / PIX / referência internacional',
        'titulo':'Bilhete Único de São Paulo é citado pela UITP e Pix aparece entre alternativas para o transporte público',
        'url':new_url,
        'fonte':'diariodotransporte.com.br',
        'id':f'achado-{len(items)+1:02d}',
        'resumo':'O Bilhete Único de São Paulo foi citado pela UITP entre referências mundiais de bilhetagem, enquanto Pix aparece como alternativa de pagamento no transporte público.',
        'impacto':'É achado incremental de 10/10 e reforça o cluster de bilhetagem digital/open payment, com conexão direta entre tecnologia, referência internacional e meios de pagamento brasileiros.',
        'tipo':'Ecossistema / imprensa setorial'
    })
# normalize ids
for i,it in enumerate(items,1): it['id']=f'achado-{i:02d}'
SEL.write_text(json.dumps(items,ensure_ascii=False,indent=2),'utf-8')
companies=list(csv.DictReader((ROOT/'fontes/associadas_abtec_oficial.csv').open(encoding='utf-8')))
social=json.loads((ROOT/'buscas/sociais_associadas_2026-10-10.json').read_text('utf-8'))

def esc(s): return html.escape(str(s or ''),quote=True)
def slug(s):
    s=str(s).lower()
    for a,b in {'á':'a','à':'a','ã':'a','â':'a','é':'e','ê':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u','ç':'c'}.items(): s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','-',s).strip('-') or 'item'
def A(h,t,cls=''):
    return f'<a class="{cls}" href="{esc(h)}" target="_blank" rel="noopener">{esc(t)}</a>' if h.startswith('http') else f'<a class="{cls}" href="{esc(h)}">{esc(t)}</a>'

def platform_label(s):
    p=s.get('label') or s.get('plataforma') or 'Canal'
    p=p.replace('www.','').replace('.com','').replace('linkedin','LinkedIn').replace('instagram','Instagram').replace('facebook','Facebook').replace('youtube','YouTube')
    return p[0].upper()+p[1:] if p else 'Canal'

by_company={}
for it in items: by_company.setdefault(it['empresa'],[]).append(it)
social_by={}
for s in social: social_by.setdefault(s['empresa'],[]).append(s)
site={c['nome_oficial']:c['site'] for c in companies}
# Cluster definitions. Alphabetical order in UI.
cluster_defs=[
 {'id':'apps-plataformas','titulo':'Apps e plataformas de confiança operacional','themes':['Tempo real / internacionalização','Apps de mobilidade','Smart cities','Mobilidade inteligente']},
 {'id':'bilhetagem-open-payment','titulo':'Bilhetagem digital, Pix e open payment','themes':['PIX no validador','Carteira digital','Bilhetagem digital','Bilhetagem / Lat.Bus','Cashback tarifário digital','Bilhetagem / PIX / referência internacional']},
 {'id':'dados-ia-sensores','titulo':'Dados, IA, sensores e biometria','themes':['IA / gestão','Big data / bilhetagem','Reconhecimento facial','Segurança / tecnologia']},
 {'id':'governanca-transparencia','titulo':'Governança de dados e transparência pública','themes':['Governança de dados','Transparência / ENMU','Big data / bilhetagem']},
 {'id':'internacionalizacao-vitrine','titulo':'Tecnologia brasileira em vitrine nacional e internacional','themes':['Internacionalização','Tempo real / internacionalização','Apps de mobilidade','Lat.Bus / tecnologia','Smart cities']},
 {'id':'sistemas-integracao','titulo':'Sistemas integrados e gestão operacional','themes':['Sistema integrado','Integração de sistemas','Mobilidade inteligente']},
]
cluster_text={
 'apps-plataformas':('Apps e plataformas aparecem como camada de previsibilidade, informação ao usuário e confiança operacional.','Acompanhar qualidade dos dados, SLA de informação ao passageiro e integrações com operadores/gestores.'),
 'bilhetagem-open-payment':('Bilhetagem, Pix, cashback e carteiras digitais formam o cluster mais tangível de tecnologia aplicada à tarifa.','Organizar pasta ABtec Mobilidade sobre open payment brasileiro, inclusão financeira, cashback tarifário e bilhetagem como infraestrutura de dados.'),
 'dados-ia-sensores':('IA, big data, reconhecimento facial e sensores aparecem como promessa de gestão, mas exigem separar caso concreto de discurso genérico.','Definir critérios de evidência: implantação real, cliente/município, dado mensurável, impacto operacional e governança/privacidade.'),
 'governanca-transparencia':('A ABtec Mobilidade já aparece defendendo tecnologia e governança de dados como resposta a falhas de transparência.','É cluster institucional forte para posicionamento público da entidade, mas ainda precisa recorrência maior para virar tendência de mercado.'),
 'internacionalizacao-vitrine':('Empresas brasileiras aparecem em eventos, implantações e vitrines fora de seus mercados tradicionais.','Monitorar como narrativa de indústria brasileira de tecnologia para mobilidade, exportação e competitividade.'),
 'sistemas-integracao':('Integração de sistemas aparece como base invisível para bilhetagem, dados, fiscalização e gestão de rede.','Pode virar pasta técnica permanente da ABtec Mobilidade: interoperabilidade, APIs, backoffice e padrões de integração.'),
}
# Criteria per cluster; mature trend candidate only 4/5 or 5/5.
def score_cluster(achados):
    companies=set(x['empresa'] for x in achados)
    sources=set(x['fonte'] for x in achados)
    criteria=[]
    criteria.append(('Volume', len(achados)>=3, f'{len(achados)} achados'))
    criteria.append(('Recorrência', len(companies)>=2 and len(sources)>=2, f'{len(companies)} atores / {len(sources)} fontes'))
    criteria.append(('Atualidade', any(('2026/10/' in x['url'] or '2026-10' in x['url']) for x in achados), 'sinal em outubro/2026' if any(('2026/10/' in x['url'] or '2026-10' in x['url']) for x in achados) else 'sem sinal novo na semana'))
    criteria.append(('Aderência ABtec Mobilidade', any(k in (x['tema']+' '+x['resumo']).lower() for x in achados for k in ['bilhetagem','pix','dados','ia','tecnologia','smart','integração','mobilidade']), 'tecnologia aplicada à mobilidade'))
    criteria.append(('Impacto setorial', any(k in (x['impacto']+' '+x['resumo']).lower() for x in achados for k in ['política','tarifa','governança','operação','usuário','pagamento','transparência','internacional']), 'impacto em política/operação/usuário/mercado'))
    return criteria
clusters=[]
for c in cluster_defs:
    ach=[it for it in items if it['tema'] in c['themes']]
    if ach:
        crit=score_cluster(ach)
        score=sum(1 for _,ok,_ in crit if ok)
        clusters.append({**c,'achados':ach,'criteria':crit,'score':score,'status':'Candidato a tendência' if score>=4 else 'Cluster em observação'})
clusters=sorted(clusters,key=lambda x:x['titulo'])
source_groups=[
 ('Instituições e entidades brasileiras','https://www.antp.org.br/','ANTP'),('Instituições e entidades brasileiras','https://www.ntu.org.br/','NTU'),('Instituições e entidades brasileiras','https://www.antptrilhos.org.br/','ANPTrilhos'),('Instituições e entidades brasileiras','https://www.bndes.gov.br/','BNDES'),('Instituições e entidades brasileiras','https://www.gov.br/cidades/pt-br','Ministério das Cidades'),
 ('Pesquisa, smart cities e mobilidade','https://www.wribrasil.org.br/','WRI Brasil'),('Pesquisa, smart cities e mobilidade','https://itdpbrasil.org/','ITDP Brasil'),('Pesquisa, smart cities e mobilidade','https://www.mobilize.org.br/','Mobilize'),('Pesquisa, smart cities e mobilidade','https://portal.connectedsmartcities.com.br/','Connected Smart Cities'),
 ('Imprensa setorial e blogs','https://diariodotransporte.com.br/','Diário do Transporte'),('Imprensa setorial e blogs','https://technibus.com.br/','Technibus'),('Imprensa setorial e blogs','https://viatrolebus.com.br/','Via Trolebus'),('Imprensa setorial e blogs','https://frotacia.com.br/','Frota&Cia'),('Imprensa setorial e blogs','https://www.baguete.com.br/','Baguete')]
css='''
:root{--navy:#10243f;--blue:#1167b1;--cyan:#1ab7c8;--green:#00a884;--amber:#f4a340;--red:#c43d32;--ink:#17212b;--muted:#667787;--line:#dbe7ef;--bg:#f5f8fb;--soft:#fbfdff}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);font-family:Inter,Arial,Helvetica,sans-serif;color:var(--ink);line-height:1.5}.wrap{max-width:1080px;margin:auto;background:#fff;min-height:100vh;padding:24px}.bar{height:10px;background:linear-gradient(90deg,var(--navy),var(--blue),var(--cyan));margin:-24px -24px 24px}.hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.title{font-size:32px;line-height:1;font-weight:950;color:var(--navy);text-transform:uppercase}.subtitle{margin-top:10px;color:var(--muted);font-size:15px}.date{margin-top:8px;font-weight:850}.logo{border:2px solid var(--blue);border-radius:16px;padding:10px 12px;background:#fff;color:var(--blue);font-weight:950;text-align:center}.intro,.summary,.section{border:1px solid var(--line);border-radius:18px;background:var(--soft);padding:16px;margin:16px 0}.topfolders{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:14px 0}.folder{border:1px solid var(--line);border-radius:16px;background:#fff;overflow:hidden}.folder summary{cursor:pointer;padding:12px 14px;font-weight:950;color:var(--navy);list-style:none}.folder summary::-webkit-details-marker{display:none}.folder .inside{border-top:1px solid var(--line);padding:10px;display:flex;gap:8px;flex-wrap:wrap}.jump,.chips,.btnrow{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}.jump a,.chip,.smallbtn{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#fff;color:var(--blue);text-decoration:none;font-weight:850}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card,.clustercard{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:12px 0;break-inside:avoid}.clustercard{border-left:6px solid var(--cyan)}.badge{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:900;background:#e8f4ff;color:var(--blue);border:1px solid #b9d8f2}.badge.cluster{background:#eef8ff;color:#0a4e88;border-color:#b9d8f2}.badge.candidate{background:#e9fbf7;color:#08745f;border-color:#bde9dd}.meta{margin:8px 0;color:var(--muted);font-size:13px;font-weight:750}.card h3{margin:8px 0;color:var(--navy);font-size:18px;line-height:1.15}.clustercard h3{margin:8px 0 10px;color:var(--navy);font-size:23px;line-height:1.08;border-bottom:2px solid #d8eef5;padding-bottom:8px}.field{margin:8px 0}.btn{display:inline-block;margin-top:8px;border-radius:999px;padding:9px 13px;background:var(--blue);color:white;font-weight:900;text-decoration:none}.clusterlink{display:inline-block;margin:4px 4px 0 0;border-radius:999px;padding:7px 10px;background:#f1fbfd;border:1px solid #bcecf2;color:#0c6672;text-decoration:none;font-size:13px;font-weight:850}.scorebar{display:flex;height:14px;border-radius:999px;overflow:hidden;border:1px solid var(--line);background:#edf2f5;margin:10px 0}.scorebar span{flex:1;border-right:1px solid #fff;background:#d4dde5}.scorebar span.on{background:var(--green)}.scorebar span.mid{background:var(--amber)}.criteria{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:6px;margin-top:8px}.criterion{border:1px solid var(--line);border-radius:12px;padding:8px;background:#fff;font-size:12px}.criterion.ok{border-color:#bde9dd;background:#f0fbf7}.foot{border-top:1px solid var(--line);margin-top:20px;padding-top:12px;color:var(--muted);font-size:13px}@media(max-width:720px){.wrap{padding:18px}.bar{margin:-18px -18px 20px}.hero{display:block}.title{font-size:27px}.logo{display:inline-block;margin-top:12px}.clustercard h3{font-size:20px}}
'''
parts=[f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade — teste analítico {DATE}</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div>']
parts.append('<section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Smart cities e tecnologias aplicadas à mobilidade no Brasil — inteligência semanal para ABtec Mobilidade</div><div class="date">Teste analítico · 10 de outubro de 2026 · janela: últimos 12 meses</div></div><div class="logo">ABtec<br>Mobilidade</div></section>')
parts.append(f'<section class="intro"><strong>Teste editorial com conteúdo vasculhado.</strong> Esta versão reúne {len(items)} achados validados. De ontem para hoje, o achado novo útil foi o Bilhete Único/Pix no Diário do Transporte; o cashback de Natal/RN já está incorporado como tecnologia tarifária digital. Os blocos abaixo são <b>clusters temáticos</b>; só viram tendência quando atingem critérios mínimos explicados na barra de maturidade.</section>')
# top dropdowns
parts.append('<section class="topfolders" aria-label="Pastas suspensas do Radar ABtec Mobilidade">')
parts.append('<details class="folder" open><summary>Clusters temáticos</summary><div class="inside">')
for c in clusters: parts.append(A('#cluster-'+c['id'],c['titulo'],'smallbtn'))
parts.append('</div></details>')
parts.append('<details class="folder"><summary>Associadas e canais</summary><div class="inside">')
for c in companies: parts.append(A('#assoc-'+slug(c['nome_oficial']),c['nome_oficial'],'smallbtn'))
parts.append('</div></details>')
parts.append('<details class="folder"><summary>Fontes brasileiras</summary><div class="inside"><a class="smallbtn" href="#fontes">Instituições, pesquisa, imprensa e blogs</a><a class="smallbtn" href="#metodo">Método e critérios</a></div></details>')
parts.append('</section>')
parts.append('<section class="section" id="clusters"><h2>Clusters temáticos em ordem alfabética</h2><p><b>Importante:</b> cluster não é tendência. A barra mostra cinco critérios: volume, recorrência, atualidade, aderência à ABtec Mobilidade e impacto setorial. Quatro ou cinco critérios acesos indicam <b>candidato a tendência</b>; abaixo disso permanece como <b>cluster em observação</b>.</p>')
for c in clusters:
    leitura,uso=cluster_text.get(c['id'],('Cluster identificado a partir dos achados curados.','Monitorar nas próximas rodadas.'))
    badgecls='candidate' if c['score']>=4 else 'cluster'
    parts.append(f'<article class="clustercard" id="cluster-{c["id"]}"><span class="badge {badgecls}">{esc(c["status"])} · {c["score"]}/5 critérios</span><h3>{esc(c["titulo"])}</h3>')
    parts.append('<div class="scorebar" title="Maturidade do cluster">')
    for idx,(_,ok,_) in enumerate(c['criteria']):
        cls='on' if ok and c['score']>=4 else 'mid' if ok else ''
        parts.append(f'<span class="{cls}"></span>')
    parts.append('</div><div class="criteria">')
    for label,ok,detail in c['criteria']:
        parts.append(f'<div class="criterion {"ok" if ok else ""}"><b>{"✓" if ok else "○"} {esc(label)}</b><br>{esc(detail)}</div>')
    parts.append('</div>')
    parts.append(f'<div class="field"><b>Leitura:</b> {esc(leitura)}</div><div class="field"><b>Uso para ABtec Mobilidade:</b> {esc(uso)}</div><div class="field"><b>Achados do cluster:</b><br>')
    for it in c['achados']: parts.append(f'<a class="clusterlink" href="#achado-{esc(it["id"])}">{esc(it["empresa"])} · {esc(it["tema"])}</a>')
    parts.append('</div></article>')
parts.append('</section>')
parts.append('<section class="summary"><h2>Resumo executivo</h2><ul><li>O incremental de ontem para hoje trouxe um achado forte de bilhetagem/open payment: Bilhete Único citado pela UITP e Pix como alternativa no transporte público.</li><li>O caso Natal/RN cashback tem tecnologia porque depende de bilhetagem/cartão eletrônico, regras de elegibilidade e crédito posterior.</li><li>Os clusters mais maduros hoje são bilhetagem/open payment e tecnologia brasileira em vitrine nacional/internacional; ainda assim aparecem como candidatos, não como tendência consolidada.</li><li>CittaMobi permanece fora das associadas até validação da relação societária/associativa com Cittati.</li></ul></section>')
# associadas
parts.append('<section class="section" id="associadas"><h2>Associadas e canais oficiais</h2><p>Nesta seção ficam apenas canais de comunicação e achados por associada. Botões de clusters foram removidos daqui para não misturar navegação editorial com canais oficiais.</p>')
for c in companies:
    name=c['nome_oficial']; parts.append(f'<section id="assoc-{slug(name)}"><h3>{esc(name)}</h3><div class="btnrow">{A(c["site"],"Site oficial","smallbtn")}')
    for s in social_by.get(name,[]): parts.append(A(s['url'],platform_label(s),'smallbtn'))
    parts.append('</div>')
    if name in by_company:
        for it in by_company[name]:
            parts.append(f'<article class="card" id="achado-{esc(it["id"])}"><span class="badge">{esc(it["tipo"])}</span><div class="meta">{esc(it["empresa"])} | {esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3><div class="field"><b>Resumo:</b> {esc(it["resumo"])}</div><div class="field"><b>Por que importa:</b> {esc(it["impacto"])}</div>{A(it["url"],"Abrir fonte","btn")}</article>')
    else:
        parts.append('<article class="card"><span class="badge">Monitoramento</span><h3>Sem achado externo curado nesta prévia</h3><div class="field">Associada mapeada por site/canais; entra na próxima rodada de imprensa, blogs e redes sociais.</div></article>')
    parts.append('</section>')
# ecossistema outside assoc
extras=[it for it in items if it['empresa'] not in site]
if extras:
    parts.append('<section id="assoc-ecossistema-smart-cities"><h3>Ecossistema Smart Cities e mobilidade digital</h3><p class="meta">Achados relevantes fora das associadas, mantidos separados para não atribuir vínculo indevido.</p>')
    for it in extras:
        parts.append(f'<article class="card" id="achado-{esc(it["id"])}"><span class="badge">{esc(it["tipo"])}</span><div class="meta">{esc(it["empresa"])} | {esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3><div class="field"><b>Resumo:</b> {esc(it["resumo"])}</div><div class="field"><b>Por que importa:</b> {esc(it["impacto"])}</div>{A(it["url"],"Abrir fonte","btn")}</article>')
    parts.append('</section>')
parts.append('</section>')
# sources
parts.append('<section class="section" id="fontes"><h2>Fontes brasileiras para seguir</h2><p>Base inicial para monitoramento da ABtec Mobilidade: instituições, pesquisa, imprensa e blogs de tecnologia/mobilidade.</p><div class="grid">')
for group in ['Instituições e entidades brasileiras','Pesquisa, smart cities e mobilidade','Imprensa setorial e blogs']:
    parts.append(f'<article class="card"><h3>{group}</h3><div class="btnrow">')
    for g,u,n in source_groups:
        if g==group: parts.append(A(u,n,'smallbtn'))
    parts.append('</div></article>')
parts.append('</div></section>')
parts.append('<section class="section" id="metodo"><h2>Método e critérios</h2><ul><li>Janela máxima: 12 meses.</li><li>Incremental 10/10→11/10: 12 resultados brutos, 1 novo achado útil incorporado; o restante era rotina operacional, duplicidade ou baixo alinhamento.</li><li>Critérios de tendência: volume, recorrência, atualidade, aderência à ABtec Mobilidade e impacto setorial. A barra só fica verde quando o cluster soma 4 ou 5 critérios.</li><li>Clusters ficam em ordem alfabética no topo, em pastas suspensas.</li><li>Usar sempre ABtec Mobilidade no texto editorial.</li></ul></section>')
parts.append('<footer class="foot"><p><strong>Nota:</strong> protótipo público de teste para organização de inteligência. Antes de uso institucional, validar tom, prioridades e sensibilidade comercial com ABtec Mobilidade.</p></footer></main></body></html>')
html_out=''.join(parts)
for path in [ROOT/'prototipos/layout-semanal/index.html', ROOT/'edicoes-semanais'/DATE/'index.html']:
    path.write_text(html_out,'utf-8')
(ROOT/'edicoes-semanais'/DATE/'clusters_tematicos.json').write_text(json.dumps(clusters,ensure_ascii=False,indent=2),'utf-8')
home=(ROOT/'index.html').read_text('utf-8') if (ROOT/'index.html').exists() else ''
home=home.replace('Sugestão de pastas ABtec','Clusters ABtec Mobilidade').replace('para ABtec</div>','para ABtec Mobilidade</div>')
(ROOT/'index.html').write_text(home,'utf-8')
print(json.dumps({'items':len(items),'clusters':len(clusters),'candidates':sum(1 for c in clusters if c['score']>=4),'href_empty':html_out.count('href="#"'),'trend_validada':html_out.count('Tendência validada'),'abtec_solo':html_out.count(' ABtec '),'cashback':html_out.lower().count('cashback'),'bilhete_unico':html_out.count('Bilhete Único')},ensure_ascii=False,indent=2))
