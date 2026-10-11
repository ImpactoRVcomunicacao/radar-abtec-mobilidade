#!/usr/bin/env python3
from pathlib import Path
import csv,json,html,re,datetime
ROOT=Path('/opt/data/abtec_mobilidade_inteligencia')
DATE='2026-10-10'
OUT=ROOT/'edicoes-semanais'/DATE
items=json.loads((OUT/'selecionados_curados.json').read_text('utf-8'))
companies=list(csv.DictReader((ROOT/'fontes'/'associadas_abtec_oficial.csv').open(encoding='utf-8')))
social=json.loads((ROOT/'buscas'/f'sociais_associadas_{DATE}.json').read_text('utf-8'))

def esc(s): return html.escape(str(s or ''),quote=True)
def slug(s):
    s=str(s).lower()
    for a,b in {'á':'a','à':'a','ã':'a','â':'a','é':'e','ê':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u','ç':'c'}.items(): s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','-',s).strip('-') or 'item'
def A(h,t,cls=''):
    return f'<a class="{cls}" href="{esc(h)}" target="_blank" rel="noopener">{esc(t)}</a>' if str(h).startswith('http') else f'<a class="{cls}" href="{esc(h)}">{esc(t)}</a>'
def plat_label(p):
    p=p.replace('www.','').replace('.com','').replace('.br','')
    return {'linkedin':'LinkedIn','facebook':'Facebook','instagram':'Instagram','youtube':'YouTube'}.get(p,p.title())
# Correções editoriais pontuais
for it in items:
    if it['titulo'].startswith('Mais.Mobi estreia'):
        it['resumo']='A Mais.Mobi/Prodata apareceu no Smart City Expo Curitiba 2026 com soluções de mobilidade, conectando a associada ao ecossistema brasileiro de cidades inteligentes.'
        it['impacto']='É um achado de associada em ambiente de smart cities, útil para monitorar posicionamento de mercado e narrativa de inovação urbana.'
    if 'Cittamobi' in it['titulo']:
        it['empresa']='Ecossistema Smart Cities'
        it['tipo']='Ecossistema / fora das associadas até validação'
        it['resumo']='O CittaMobi aparece como solução tecnológica para cidades inteligentes em mobilidade urbana, mas fica fora do bloco de associadas até validação formal de vínculo com Cittati/ABtec.'
        it['impacto']='Serve como sinal de mercado e referência temática, não como evidência de associada.'
# Clusters em ordem alfabética
cluster_defs={
 'Apps, plataformas e informação ao usuário': ['Apps de mobilidade','Mobilidade inteligente','Smart cities','Sistema integrado'],
 'Bilhetagem digital, pagamentos e open payment': ['Bilhetagem / Lat.Bus','PIX no validador','Bilhetagem digital','Carteira digital'],
 'Dados, integração e governança pública': ['Governança de dados','Transparência / ENMU','Big data / bilhetagem','Integração de sistemas'],
 'IA, biometria e segurança operacional': ['IA / gestão','Reconhecimento facial','Segurança / tecnologia'],
 'Internacionalização e vitrine setorial': ['Internacionalização','Lat.Bus / tecnologia','Tempo real / internacionalização'],
 'Regulação, produto e infraestrutura tecnológica': ['Sistema integrado']
}
cluster_notes={
 'Apps, plataformas e informação ao usuário':'Agrupa aplicativos, plataformas e soluções que aproximam gestor, operador e passageiro por informação, tempo real e experiência de uso.',
 'Bilhetagem digital, pagamentos e open payment':'Reúne pagamento digital, Pix, carteiras digitais, validadores e a evolução da bilhetagem como infraestrutura de relacionamento e dados.',
 'Dados, integração e governança pública':'Concentra achados sobre transparência, ENMU, integração de sistemas, big data e uso de dados para governança do transporte.',
 'IA, biometria e segurança operacional':'Observa inteligência artificial, reconhecimento facial, sensores e tecnologias de segurança/controle operacional.',
 'Internacionalização e vitrine setorial':'Monitora presença das associadas em feiras, mercados externos e narrativas de exportação de tecnologia brasileira.',
 'Regulação, produto e infraestrutura tecnológica':'Espaço para tecnologias proprietárias ou produtos oficiais que ainda não formam tendência, mas devem entrar no radar.'
}
# item clusters; item can be in first matching cluster
item_cluster={}
for cname,themes in cluster_defs.items():
    for it in items:
        if it['tema'] in themes and it['id'] not in item_cluster:
            item_cluster[it['id']]=cname
for it in items:
    item_cluster.setdefault(it['id'],'Regulação, produto e infraestrutura tecnológica')
clusters={c:[] for c in sorted(cluster_defs)}
for it in items:
    clusters.setdefault(item_cluster[it['id']],[]).append(it)
# critérios de tendência candidata (não validados como tendência final)
ref=datetime.date(2026,10,10)
def parse_date(url):
    m=re.search(r'/((20\d{2})/(\d{2})/(\d{2}))/',url)
    if m:
        try: return datetime.date(int(m.group(2)),int(m.group(3)),int(m.group(4)))
        except: pass
    return None
def maturity(cname, arr):
    empresas={x['empresa'] for x in arr}; fontes={x['fonte'] for x in arr}; temas={x['tema'] for x in arr}
    score=0; crit=[]
    ev=min(20, len(arr)*5); score+=ev; crit.append(('Evidências',ev,20,f'{len(arr)} achado(s)'))
    comp=20 if len(empresas)>=3 else 14 if len(empresas)==2 else 6 if len(empresas)==1 else 0; score+=comp; crit.append(('Empresas/ecossistema',comp,20,f'{len(empresas)} ator(es)'))
    src=15 if len(fontes)>=3 else 10 if len(fontes)==2 else 5 if len(fontes)==1 else 0; score+=src; crit.append(('Diversidade de fontes',src,15,f'{len(fontes)} fonte(s)'))
    inst=15 if any(x['empresa']=='ABtec Mobilidade' or x['fonte'] in ['antp.org.br','technibus.com.br','diariodotransporte.com.br'] for x in arr) else 0; score+=inst; crit.append(('Peso institucional/setorial',inst,15,'ABtec/ANTP/imprensa setorial' if inst else 'sem evidência institucional'))
    strat=20 if cname in ['Bilhetagem digital, pagamentos e open payment','Dados, integração e governança pública','Apps, plataformas e informação ao usuário'] else 15; score+=strat; crit.append(('Aderência à agenda ABtec',strat,20,'alta' if strat==20 else 'média'))
    dates=[parse_date(x['url']) for x in arr]; dates=[d for d in dates if d]
    rec=10 if any((ref-d).days<=180 for d in dates) else 5 if dates else 0; score+=rec; crit.append(('Recência',rec,10,'há achado recente' if rec==10 else 'achados dentro de 1 ano'))
    score=min(score,100)
    label='Tendência candidata' if score>=75 else 'Sinal emergente' if score>=50 else 'Assunto monitorado'
    color='#00a884' if score>=75 else '#f4a340' if score>=50 else '#94a3b8'
    return {'score':score,'label':label,'color':color,'criteria':crit,'empresas':sorted(empresas),'fontes':sorted(fontes),'temas':sorted(temas)}
cluster_maturity={c:maturity(c,a) for c,a in clusters.items() if a}
by_company={}
for it in items: by_company.setdefault(it['empresa'],[]).append(it)
social_by={}
for s in social: social_by.setdefault(s['empresa'],[]).append(s)
# include ABtec first + official associated
official_names=[c['nome_oficial'] for c in companies]
css='''
:root{--navy:#10243f;--blue:#1167b1;--cyan:#1ab7c8;--green:#00a884;--amber:#f4a340;--red:#c43d32;--ink:#17212b;--muted:#667787;--line:#dbe7ef;--bg:#f5f8fb;--soft:#fbfdff}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);font-family:Inter,Arial,Helvetica,sans-serif;color:var(--ink);line-height:1.5}.wrap{max-width:1080px;margin:auto;background:#fff;min-height:100vh;padding:24px}.bar{height:10px;background:linear-gradient(90deg,var(--navy),var(--blue),var(--cyan));margin:-24px -24px 24px}.hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.title{font-size:32px;line-height:1;font-weight:950;color:var(--navy);text-transform:uppercase}.subtitle{margin-top:10px;color:var(--muted);font-size:15px}.date{margin-top:8px;font-weight:850}.logo{border:2px solid var(--blue);border-radius:16px;padding:10px 12px;background:#fff;color:var(--blue);font-weight:950;text-align:center}.intro,.summary,.section{border:1px solid var(--line);border-radius:18px;background:var(--soft);padding:16px;margin:16px 0}.jump,.chips,.btnrow{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}.jump a,.chip,.smallbtn{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#fff;color:var(--blue);text-decoration:none;font-weight:850}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card,.clusterbox{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:12px 0;break-inside:avoid}.clusterbox{border-left:6px solid var(--blue)}.badge{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:900;background:#e8f4ff;color:var(--blue);border:1px solid #b9d8f2}.badge.eco{background:#fff7e8;color:#9a5b00;border-color:#ffd796}.meta{margin:8px 0;color:var(--muted);font-size:13px;font-weight:750}.card h3{margin:8px 0;color:var(--navy);font-size:18px;line-height:1.15}.cluster-title{margin:4px 0;color:var(--navy);font-size:23px;line-height:1.05;font-weight:950}.cluster-sub{font-size:15px;color:var(--ink);font-weight:650}.field{margin:8px 0}.btn{display:inline-block;margin-top:8px;border-radius:999px;padding:9px 13px;background:var(--blue);color:white;font-weight:900;text-decoration:none}.barbox{height:14px;background:#e6edf4;border-radius:999px;overflow:hidden;border:1px solid var(--line);margin:8px 0}.barfill{height:100%;border-radius:999px}.criteria{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin-top:8px}.criterion{border:1px solid var(--line);border-radius:12px;padding:8px;background:#fbfdff;font-size:12px}.details{border:1px solid var(--line);border-radius:14px;background:#fff;margin:10px 0;overflow:hidden}.details summary{cursor:pointer;padding:12px 14px;font-weight:950;color:var(--navy);font-size:18px;background:#f4f9fc}.details .inside{padding:0 14px 14px}.socialblock{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px;margin:8px 0}.foot{border-top:1px solid var(--line);margin-top:20px;padding-top:12px;color:var(--muted);font-size:13px}@media(max-width:720px){.wrap{padding:18px}.bar{margin:-18px -18px 20px}.hero{display:block}.title{font-size:27px}.logo{display:inline-block;margin-top:12px}.cluster-title{font-size:20px}}
'''
parts=[f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade — clusters {DATE}</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div>']
parts.append('<section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Smart cities e tecnologias aplicadas à mobilidade no Brasil — inteligência semanal para ABtec</div><div class="date">Teste analítico · 10 de outubro de 2026 · janela máxima: últimos 12 meses</div></div><div class="logo">ABtec<br>Mobilidade</div></section>')
parts.append('<section class="intro"><strong>Versão revisada.</strong> Esta leitura separa <b>assuntos clusterizados</b> de <b>tendências</b>. Nem todo achado é tendência. A barra de maturidade abaixo mostra quando um cluster começa a se aproximar de uma tendência candidata, com critérios explícitos.</section>')
parts.append('<nav class="jump"><a href="#criterios">Critérios de tendência</a><a href="#clusters">Clusters temáticos</a><a href="#sociais">Redes sociais</a><a href="#associadas">Associadas</a><a href="#ecossistema">Ecossistema fora das associadas</a></nav>')
parts.append('<section class="section" id="criterios"><h2>Quando um cluster vira tendência?</h2><p>Por enquanto, não estamos chamando nada de “tendência validada”. Usamos uma escala de <b>maturidade do sinal</b>. A barra fica verde quando o cluster soma critérios suficientes para ser tratado como <b>tendência candidata</b>, ainda sujeita à análise editorial e acompanhamento semanal.</p><div class="grid"><article class="card"><h3>Critérios usados</h3><ul><li>Volume de evidências</li><li>Mais de uma empresa/ecossistema envolvido</li><li>Diversidade de fontes</li><li>Peso institucional ou setorial</li><li>Aderência à agenda ABtec</li><li>Recência dentro da janela de 1 ano</li></ul></article><article class="card"><h3>Leitura da barra</h3><ul><li>0–49: assunto monitorado</li><li>50–74: sinal emergente</li><li>75–100: tendência candidata</li></ul></article></div></section>')
parts.append('<section class="section" id="clusters"><h2>Clusters temáticos em ordem alfabética</h2><p>Use estas pastas para organizar o radar. Cada pasta abre os achados relacionados e mostra a maturidade do sinal.</p>')
for cname in sorted(clusters):
    arr=clusters[cname]
    if not arr: continue
    mat=cluster_maturity[cname]
    parts.append(f'<details class="details" open><summary>{esc(cname)} · {len(arr)} achado(s)</summary><div class="inside"><article class="clusterbox"><div class="cluster-title">{esc(cname)}</div><div class="cluster-sub">{esc(cluster_notes.get(cname,"Assunto em monitoramento."))}</div><div class="meta"><b>Maturidade do sinal:</b> {esc(mat["label"])} · {mat["score"]}/100</div><div class="barbox"><div class="barfill" style="width:{mat["score"]}%;background:{mat["color"]}"></div></div><div class="criteria">')
    for label,score,total,note in mat['criteria']:
        parts.append(f'<div class="criterion"><b>{esc(label)}</b><br>{score}/{total}<br><span>{esc(note)}</span></div>')
    parts.append('</div></article>')
    for it in arr:
        badgecls=' eco' if it['empresa']=='Ecossistema Smart Cities' else ''
        parts.append(f'<article class="card" id="achado-{esc(it["id"])}"><span class="badge{badgecls}">{esc(it["tipo"])}</span><div class="meta">{esc(it["empresa"])} | {esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3><div class="field"><b>Resumo:</b> {esc(it["resumo"])}</div><div class="field"><b>Por que importa:</b> {esc(it["impacto"])}</div>{A(it["url"],"Abrir fonte","btn")}</article>')
    parts.append('</div></details>')
parts.append('</section>')
parts.append('<section class="section" id="sociais"><h2>Redes sociais e canais oficiais mapeados</h2><p>Redes sociais entram como camada de monitoramento. Nesta prévia, os links vêm dos sites oficiais ou da página da ABtec.</p><div class="grid">')
for name in ['ABtec Mobilidade']+[n for n in official_names if n!='ABtec Mobilidade']:
    links=social_by.get(name,[])
    if not links: continue
    parts.append(f'<article class="socialblock"><h3>{esc(name)}</h3><div class="btnrow">')
    for s in links:
        label=s.get('label') or plat_label(s['plataforma'])
        parts.append(A(s['url'],label,'smallbtn'))
    parts.append('</div></article>')
parts.append('</div></section>')
parts.append('<section class="section" id="associadas"><h2>Associadas oficiais ABtec</h2><p>Nesta seção, os botões são apenas canais de comunicação: site e redes oficiais. Os achados aparecem como cards, mas sem botões de clusters dentro do bloco da empresa.</p>')
site={c['nome_oficial']:c['site'] for c in companies}
for name in official_names:
    if name=='ABtec Mobilidade': continue
    parts.append(f'<details class="details"><summary>{esc(name)} · {len(by_company.get(name,[]))} achado(s)</summary><div class="inside"><div class="btnrow">{A(site.get(name,""),"Site oficial","smallbtn") if site.get(name) else ""}')
    for s in social_by.get(name,[]): parts.append(A(s['url'],s.get('label') or plat_label(s['plataforma']),'smallbtn'))
    parts.append('</div>')
    for it in by_company.get(name,[]):
        parts.append(f'<article class="card"><div class="meta">{esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3>{A(it["url"],"Abrir fonte","btn")}</article>')
    if not by_company.get(name): parts.append('<article class="card"><h3>Sem achado externo curado nesta prévia</h3><p>Empresa mapeada por site oficial e canais. Entra nas próximas rodadas de imprensa e redes.</p></article>')
    parts.append('</div></details>')
parts.append('</section>')
parts.append('<section class="section" id="ecossistema"><h2>Ecossistema fora das associadas / requer validação</h2><p>Itens relevantes para o mercado, mas que não devem aparecer como achados de associadas enquanto não houver vínculo formal confirmado com ABtec.</p>')
for it in by_company.get('Ecossistema Smart Cities',[]):
    parts.append(f'<article class="card"><span class="badge eco">Fora das associadas até validação</span><div class="meta">{esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3><div class="field">{esc(it["resumo"])}</div>{A(it["url"],"Abrir fonte","btn")}</article>')
parts.append('</section>')
parts.append('<section class="summary"><h2>Leitura editorial desta prévia</h2><ul><li>Os clusters mais maduros hoje são bilhetagem/open payment, dados/governança e apps/plataformas.</li><li>CittaMobi não foi atribuído à Cittati nesta versão; fica como ecossistema até validação formal.</li><li>A próxima rodada deve aprofundar redes sociais: LinkedIn da ABtec e das associadas, posts recentes e repercussão em imprensa/entidades.</li><li>O objetivo não é classificar tudo como tendência; é acumular evidências por pasta até que a barra de maturidade justifique tratar como tendência candidata.</li></ul></section>')
parts.append('<footer class="foot"><p><strong>Nota:</strong> protótipo público de teste. Janela máxima: 1 ano. Tendências aqui são hipóteses graduadas por critérios, não validações finais.</p></footer></main></body></html>')
html_out=''.join(parts)
(OUT/'index.html').write_text(html_out,'utf-8')
(ROOT/'prototipos/layout-semanal/index.html').write_text(html_out,'utf-8')
home=f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div><section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Inteligência semanal sobre smart cities e tecnologia para mobilidade no Brasil</div><div class="date">Página inicial pública de teste</div></div><div class="logo">ABtec<br>Mobilidade</div></section><section class="intro"><p>Ambiente separado do PANORAMA para organizar achados, clusters temáticos e tendências candidatas para a ABtec Mobilidade.</p><div class="btnrow"><a class="btn" href="edicoes-semanais/{DATE}/">Abrir teste analítico</a><a class="smallbtn" href="prototipos/layout-semanal/">Abrir protótipo de layout</a><a class="smallbtn" href="fontes/associadas_abtec_oficial.csv">Base de associadas</a></div></section></main></body></html>'
(ROOT/'index.html').write_text(home,'utf-8')
(OUT/'clusters_maturidade.json').write_text(json.dumps({'clusters':clusters,'maturity':cluster_maturity},ensure_ascii=False,indent=2,default=str),'utf-8')
print(json.dumps({'items':len(items),'clusters':len([c for c,a in clusters.items() if a]),'cards':html_out.count('class="card"'),'details':html_out.count('<details'),'gnews':html_out.count('news.google.com'),'hrefempty':html_out.count('href="#"'),'cittamobi_in_ecosystem':'CittaMobi' in html_out and 'Ecossistema' in html_out},ensure_ascii=False,indent=2))
