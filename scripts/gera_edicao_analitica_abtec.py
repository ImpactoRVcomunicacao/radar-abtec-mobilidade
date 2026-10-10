#!/usr/bin/env python3
from pathlib import Path
import json, re, html, shutil
ROOT=Path('/opt/data/abtec_mobilidade_inteligencia')
DATE='2026-10-10'
OUT=ROOT/'edicoes-semanais'/DATE
sel=json.loads((OUT/'selecionados_curados.json').read_text('utf-8'))
companies_raw=json.loads((ROOT/'fontes/associadas_abtec_oficial.json').read_text('utf-8'))
if isinstance(companies_raw, dict):
    companies=[{'nome_oficial': companies_raw.get('entidade',{}).get('nome','ABtec Mobilidade'), 'site': companies_raw.get('entidade',{}).get('site','https://abtecbr.org/') }]
    companies += [{'nome_oficial': c.get('nome'), 'site': c.get('site','')} for c in companies_raw.get('associadas', [])]
else:
    companies=companies_raw

def esc(s): return html.escape(str(s or ''), quote=True)
def slug(s):
    s=str(s).lower()
    repl={'á':'a','à':'a','ã':'a','â':'a','é':'e','ê':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u','ç':'c'}
    for a,b in repl.items(): s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','-',s).strip('-') or 'item'

company_sites={c['nome_oficial']:c.get('site','') for c in companies}
# normalize selected company names
for item in sel:
    if item['empresa']=='Prodata': item['empresa']='Prodata Mobility Brasil'
    if item['empresa']=='Cittati / CittaMobi': item['empresa']='Cittati'

trend_defs=[
    {
        'id':'governanca-dados-transparencia',
        'titulo':'Governança de dados e transparência do transporte público',
        'criterios':['ABtec Mobilidade'],
        'keywords':['transparência','governança','dados','ENMU','tecnologia'],
        'leitura':'A ABtec aparece com uma narrativa institucional forte: tecnologia como infraestrutura de governança, transparência e accountability do transporte público, não apenas como fornecimento de sistemas.',
        'uso':'Base para pasta institucional da ABtec sobre maturidade digital, transparência dos sistemas e defesa de padrões de dados para gestores públicos.'
    },
    {
        'id':'bilhetagem-pagamentos-conta-digital',
        'titulo':'Bilhetagem, pagamentos e conta digital virando camada de relacionamento',
        'criterios':['Prodata Mobility Brasil','Transdata','ONBOARD','Empresa 1'],
        'keywords':['bilhetagem','pagamento','conta digital','validadores','pix','pix'],
        'leitura':'As associadas aparecem ligadas à evolução da bilhetagem para uma plataforma mais ampla de pagamentos, identificação, integração e relacionamento com o usuário.',
        'uso':'Pasta para posicionar a ABtec em debates sobre interoperabilidade, abertura de dados, segurança transacional, inclusão digital e modernização tarifária.'
    },
    {
        'id':'dados-tempo-real-experiencia-usuario',
        'titulo':'Dados em tempo real e experiência do passageiro como infraestrutura de confiança',
        'criterios':['Bus2','Cittati'],
        'keywords':['tempo real','aplicativo','app','informação ao usuário','monitoramento','experiência'],
        'leitura':'Apps, monitoramento e informação em tempo real aparecem como elementos centrais para reduzir incerteza, aumentar confiança e melhorar a percepção do transporte coletivo.',
        'uso':'Pasta para defender tecnologia de informação ao usuário como política pública de qualidade, não apenas conveniência de aplicativo.'
    },
    {
        'id':'ia-analytics-operacao',
        'titulo':'IA, analytics e automação avançando da retórica para operação',
        'criterios':['SONDA','Planeta Informática','Cittati','Bus2'],
        'keywords':['IA','analytics','inteligência','dados','monitoramento','gestão'],
        'leitura':'A coleta mostra IA e analytics associados à eficiência operacional, atendimento, planejamento e leitura de dados — mas ainda exige separar casos concretos de discurso genérico.',
        'uso':'Pasta para mapear casos demonstráveis, riscos de hype, requisitos de governança algorítmica e oportunidades de capacitação para gestores.'
    },
    {
        'id':'associadas-exportacao-tecnologia-brasileira',
        'titulo':'Tecnologia brasileira de mobilidade ganhando vitrine regional',
        'criterios':['Bus2','SONDA','Prodata Mobility Brasil'],
        'keywords':['Paraguai','Lat.Bus','América Latina','internacionalização','brasileira'],
        'leitura':'Há sinais de empresas brasileiras levando tecnologia de mobilidade para mercados vizinhos ou ganhando visibilidade em eventos/setores regionais.',
        'uso':'Pasta para construir narrativa de indústria brasileira de tecnologia para mobilidade, exportação de soluções e protagonismo regional.'
    },
]

def matches_trend(item, t):
    hay=' '.join([item.get('empresa',''), item.get('tema',''), item.get('titulo',''), item.get('resumo',''), item.get('impacto','')]).lower()
    if item.get('empresa') in t['criterios']: return True
    return any(k.lower() in hay for k in t['keywords'])

trends=[]
for t in trend_defs:
    ach=[it for it in sel if matches_trend(it,t)]
    # remove weak broad matches: require at least 2, except ABtec governance which has direct institutional signal
    if len(ach)>=2 or t['id']=='governanca-dados-transparencia':
        tt=dict(t); tt['achados']=ach[:5]; trends.append(tt)

by_company={}
for it in sel:
    by_company.setdefault(it['empresa'],[]).append(it)
company_order=['ABtec Mobilidade','Bus2','Cittati','Empresa 1','ONBOARD','Planeta Informática','Prodata Mobility Brasil','SONDA','Transdata','Paraguai / ecossistema']
# include unknowns
for c in by_company:
    if c not in company_order: company_order.append(c)

css='''
:root{--navy:#10243f;--blue:#1167b1;--cyan:#1ab7c8;--green:#00a884;--amber:#f4a340;--red:#c43d32;--ink:#17212b;--muted:#667787;--line:#dbe7ef;--bg:#f5f8fb;--soft:#fbfdff}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);font-family:Inter,Arial,Helvetica,sans-serif;color:var(--ink);line-height:1.5}.wrap{max-width:1080px;margin:auto;background:#fff;min-height:100vh;padding:24px}.bar{height:10px;background:linear-gradient(90deg,var(--navy),var(--blue),var(--cyan));margin:-24px -24px 24px}.hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.title{font-size:32px;line-height:1;font-weight:950;color:var(--navy);text-transform:uppercase}.subtitle{margin-top:10px;color:var(--muted);font-size:15px}.date{margin-top:8px;font-weight:850}.logo{border:2px solid var(--blue);border-radius:16px;padding:10px 12px;background:#fff;color:var(--blue);font-weight:950;text-align:center}.intro,.summary,.section{border:1px solid var(--line);border-radius:18px;background:var(--soft);padding:16px;margin:16px 0}.jump,.chips,.btnrow{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}.jump a,.chip,.smallbtn{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#fff;color:var(--blue);text-decoration:none;font-weight:850}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card,.trendcard{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:12px 0;break-inside:avoid}.trendcard{border-left:5px solid var(--cyan)}.badge{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:900;background:#e8f4ff;color:var(--blue);border:1px solid #b9d8f2}.badge.trend{background:#e9fbf7;color:#08745f;border-color:#bde9dd}.meta{margin:8px 0;color:var(--muted);font-size:13px;font-weight:750}.card h3,.trendcard h3{margin:8px 0;color:var(--navy);font-size:18px;line-height:1.15}.field{margin:8px 0}.btn{display:inline-block;margin-top:8px;border-radius:999px;background:var(--navy);color:#fff;text-decoration:none;font-weight:900;padding:9px 13px}.trendbtn{display:inline-block;margin:4px 6px 0 0;border-radius:999px;background:#eef8fb;color:var(--blue);border:1px solid #bee4ec;text-decoration:none;font-weight:850;padding:7px 10px;font-size:13px}.source-list li{margin:5px 0}.empty{color:var(--muted);font-style:italic}.foot{color:var(--muted);font-size:13px;margin:24px 0 10px}@media(max-width:720px){.wrap{padding:18px}.bar{margin:-18px -18px 20px}.hero{display:block}.title{font-size:27px}.logo{margin-top:12px;display:inline-block}.jump{overflow-x:auto;flex-wrap:nowrap;padding-bottom:6px}.jump a{white-space:nowrap}}
'''

def a(href,text,cls=''):
    return f'<a class="{cls}" href="{esc(href)}">{esc(text)}</a>'

parts=[]
parts.append(f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade — prévia analítica {DATE}</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div>')
parts.append('<section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Smart cities e tecnologias aplicadas à mobilidade no Brasil — inteligência semanal para ABtec</div><div class="date">Prévia analítica · 10 de outubro de 2026</div></div><div class="logo">ABtec<br>Mobilidade</div></section>')
parts.append(f'<section class="intro"><strong>Teste editorial.</strong> Esta prévia usa {len(sel)} achados reais de sites oficiais, imprensa setorial e fontes abertas. A seção de tendências abaixo não é lista automática de matérias: é uma síntese analítica derivada dos achados curados.</section>')
parts.append('<nav class="jump" aria-label="Navegação"><a href="#tendencias">Tendências encontradas</a><a href="#associadas">Associadas e achados</a><a href="#fontes">Fontes e próximos passos</a><a href="./selecionados_curados.json">Base curada JSON</a></nav>')
# company buttons
parts.append('<section class="section"><h2>Associadas mapeadas</h2><div class="jump">')
for c in company_order:
    if c in by_company:
        parts.append(a('#assoc-'+slug(c), f'{c} ({len(by_company[c])})'))
    else:
        site=company_sites.get(c,'')
        parts.append(a(site or '#fontes', f'{c} (sem achado curado)'))
parts.append('</div><p class="meta">Botões com contagem levam aos achados desta prévia; empresas sem achado curado levam ao site oficial quando mapeado.</p></section>')
# trends
parts.append('<section class="section" id="tendencias"><h2>Tendências encontradas</h2><p>Estas tendências são agrupamentos analíticos criados a partir dos achados. Cada botão abaixo leva às matérias que sustentam a tendência.</p>')
for t in trends:
    parts.append(f'<article class="trendcard" id="trend-{t["id"]}"><span class="badge trend">Tendência</span><h3>{esc(t["titulo"])}</h3><div class="field"><b>Leitura executiva:</b> {esc(t["leitura"])}</div><div class="field"><b>Como a ABtec pode usar:</b> {esc(t["uso"])}</div><div class="field"><b>Achados que sustentam:</b><br>')
    for it in t['achados']:
        parts.append(f'<a class="trendbtn" href="#achado-{esc(it["id"])}">{esc(it["empresa"])} · {esc(it["tema"])}</a>')
    parts.append('</div></article>')
parts.append('</section>')
# summary
parts.append('<section class="summary"><h2>Resumo executivo</h2><ul>')
parts.append('<li>O material mais forte para a ABtec está na agenda de governança de dados/transparência do transporte público, com boa aderência para posicionamento institucional.</li>')
parts.append('<li>As associadas aparecem principalmente em bilhetagem/pagamentos, dados em tempo real, apps, monitoramento operacional, IA/analytics e exportação de tecnologia brasileira.</li>')
parts.append('<li>A próxima versão precisa aprofundar redes sociais e blogs especializados para separar novidade semanal de conteúdo institucional permanente.</li>')
parts.append('</ul></section>')
# by company
parts.append('<section class="section" id="associadas"><h2>Achados por associada</h2>')
for c in company_order:
    if c not in by_company: continue
    site=company_sites.get(c,'')
    parts.append(f'<section id="assoc-{slug(c)}"><h3>{esc(c)}</h3><div class="btnrow">')
    if site: parts.append(a(site,'Site oficial','smallbtn'))
    # trend buttons for this company
    for t in trends:
        if any(it['empresa']==c for it in t['achados']):
            parts.append(a('#trend-'+t['id'], 'Tendência: '+t['titulo'][:42], 'smallbtn'))
    parts.append('</div>')
    for it in by_company[c]:
        parts.append(f'<article class="card" id="achado-{esc(it["id"])}"><span class="badge">Achado curado</span><div class="meta">{esc(it["empresa"])} | {esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3><div class="field"><b>Resumo:</b> {esc(it["resumo"])}</div><div class="field"><b>Por que importa:</b> {esc(it["impacto"])}</div><a class="btn" href="{esc(it["url"])}" target="_blank" rel="noopener">Abrir fonte</a></article>')
    parts.append('</section>')
parts.append('</section>')
# sources and next
parts.append('<section class="section" id="fontes"><h2>Fontes e próximos passos de coleta</h2><div class="grid"><article class="card"><h3>Já mapeado</h3><ul><li>Site oficial ABtec e página de associadas.</li><li>Sites oficiais das associadas.</li><li>Canais sociais encontrados nos sites oficiais.</li><li>Imprensa setorial inicial: Diário do Transporte e Technibus, entre outras fontes abertas.</li></ul></article><article class="card"><h3>Próxima rodada</h3><ul><li>Revisar LinkedIn/Instagram/YouTube das associadas com busca por posts recentes.</li><li>Ampliar blogs e mídia de tecnologia, smart cities e transporte público no Brasil.</li><li>Separar conteúdo institucional permanente de novidade semanal.</li><li>Criar pastas temáticas para a ABtec a partir das tendências confirmadas.</li></ul></article></div></section>')
parts.append('<footer class="foot"><p><strong>Nota:</strong> prévia interna/pública de teste. Conteúdo sujeito a curadoria adicional, checagem de redes sociais e atualização semanal antes de uso institucional.</p></footer></main></body></html>')
html_out=''.join(parts)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'index.html').write_text(html_out,'utf-8')
(ROOT/'prototipos/layout-semanal/index.html').write_text(html_out,'utf-8')
# homepage
home=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div><section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Inteligência semanal sobre smart cities e tecnologia para mobilidade no Brasil</div><div class="date">Página inicial de teste</div></div><div class="logo">ABtec<br>Mobilidade</div></section><section class="intro"><p>Ambiente separado do PANORAMA para organizar achados, tendências e pastas estratégicas para a ABtec Mobilidade.</p><div class="btnrow"><a class="btn" href="edicoes-semanais/{DATE}/">Abrir prévia analítica</a><a class="smallbtn" href="prototipos/layout-semanal/">Abrir protótipo de layout</a><a class="smallbtn" href="fontes/associadas_abtec_oficial.csv">Base de associadas</a></div></section></main></body></html>'''
(ROOT/'index.html').write_text(home,'utf-8')
print('wrote',OUT/'index.html','cards',html_out.count('class="card"'),'trends',len(trends),'href#',html_out.count('href="#"'))
print('companies with achados', {k:len(v) for k,v in by_company.items()})
