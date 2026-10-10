#!/usr/bin/env python3
from pathlib import Path
import csv,json,html,re,shutil
ROOT=Path('/opt/data/abtec_mobilidade_inteligencia')
DATE='2026-10-10'
OUT=ROOT/'edicoes-semanais'/DATE
qa=json.loads((ROOT/'buscas'/'qa_urls_curadoria_manual_2026-10-10.json').read_text('utf-8'))
companies=list(csv.DictReader((ROOT/'fontes'/'associadas_abtec_oficial.csv').open(encoding='utf-8')))
social=json.loads((ROOT/'buscas'/f'sociais_associadas_{DATE}.json').read_text('utf-8'))

def esc(s): return html.escape(str(s or ''),quote=True)
def slug(s):
    s=str(s).lower();
    for a,b in {'á':'a','à':'a','ã':'a','â':'a','é':'e','ê':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u','ç':'c'}.items(): s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','-',s).strip('-') or 'item'
summary={
 'Governança de dados':'A ABtec conecta tecnologia, governança de dados e transparência como agenda pública do transporte coletivo.',
 'Transparência / ENMU':'A cobertura usa o ENMU como gancho para defender tecnologia na qualificação da gestão e da informação pública.',
 'Tempo real / internacionalização':'A Bus2 aparece aplicada fora do Brasil com monitoramento em tempo real de ônibus.',
 'Apps de mobilidade':'A presença da Bus2 no Paraguai reforça exportação de solução brasileira para apps de mobilidade.',
 'Big data / bilhetagem':'A bilhetagem aparece como camada de leitura inteligente da operação de ônibus.',
 'Smart cities':'O CittaMobi foi associado a uma solução tecnológica para cidades inteligentes em mobilidade urbana.',
 'Bilhetagem / Lat.Bus':'A Empresa 1 levou digitalização da bilhetagem e gestão do transporte coletivo à Lat.Bus 2026.',
 'Segurança / tecnologia':'A Empresa 1 aparece ligada ao uso de tecnologia para reforçar segurança no transporte coletivo.',
 'PIX no validador':'Florianópolis adotou pagamento por Pix no validador dos ônibus, reforçando open payment no transporte.',
 'Bilhetagem digital':'A ONBOARD posiciona dispositivo de bilhetagem digital como infraestrutura embarcada.',
 'Reconhecimento facial':'A ONBOARD apresenta reconhecimento facial como recurso de controle e segurança na operação.',
 'Sistema integrado':'A Planeta Informática apresenta sistema integrado para gestão do transporte e mobilidade.',
 'Internacionalização':'A Prodata/Mais Mobi levou tecnologia brasileira a evento internacional de transporte público.',
 'IA / gestão':'A Prodata/Mais Mobi aparece com aplicações de IA para gestão da mobilidade.',
 'Smart cities / mobilidade':'A Mais.Mobi entrou no Smart City Expo Curitiba com soluções de mobilidade.',
 'Mobilidade inteligente':'Fortaleza aparece com evolução de app de ônibus para plataforma de mobilidade inteligente com SONDA.',
 'Tecnologia / Lat.Bus':'A SONDA apresentou tecnologias para transporte e mobilidade urbana na Lat.Bus 2026.',
 'Integração de sistemas':'A Transdata destaca integração de sistemas como vetor do futuro do transporte público.',
 'Carteira digital':'Transdata aparece em caso de Carteira Google nos ônibus de Ponta Grossa.'
}
impact={
 'Governança de dados':'Sustenta pasta de transparência, dados públicos, interoperabilidade e accountability.',
 'Transparência / ENMU':'Ajuda a ABtec a se posicionar como voz técnica em maturidade digital do setor.',
 'Tempo real / internacionalização':'Mostra tecnologia brasileira com potencial de exportação regional e impacto no usuário.',
 'Apps de mobilidade':'Reforça apps como camada de confiança, previsibilidade e informação ao passageiro.',
 'Big data / bilhetagem':'Indica que bilhetagem está virando sensor urbano, não só mecanismo de cobrança.',
 'Smart cities':'Validação técnica externa é forte para a narrativa de Smart Cities aplicada à mobilidade.',
 'Bilhetagem / Lat.Bus':'A feira mostra vitrine comercial e competição tecnológica entre associadas.',
 'Segurança / tecnologia':'Segurança tende a crescer como argumento de valor em tecnologia embarcada.',
 'PIX no validador':'O Pix no validador pode ser tendência brasileira própria de inclusão em open payment.',
 'Bilhetagem digital':'Ajuda a diferenciar bilhetagem digital de bilhetagem eletrônica tradicional.',
 'Reconhecimento facial':'Tema útil para discutir biometria, segurança, privacidade e controle operacional.',
 'Sistema integrado':'Mostra espaço para monitorar empresas com menor presença de imprensa, mas oferta tecnológica relevante.',
 'Internacionalização':'Base para pasta sobre tecnologia brasileira ganhando vitrine internacional.',
 'IA / gestão':'IA aparece como agenda de produto e gestão, mas exige separar caso concreto de hype.',
 'Smart cities / mobilidade':'Conecta associadas ao ecossistema de cidades inteligentes, além do transporte tradicional.',
 'Mobilidade inteligente':'Mostra plataforma urbana de serviços e dados substituindo app meramente informativo.',
 'Tecnologia / Lat.Bus':'Sinaliza entrada de TI corporativa na agenda de transporte público.',
 'Integração de sistemas':'Integração é pré-condição para dados confiáveis, pagamento aberto e gestão multimodal.',
 'Carteira digital':'Carteiras digitais ampliam meios de pagamento e aproximam transporte de ecossistemas financeiros.'
}
items=[]
for r in qa:
    if r['status']!='ok': continue
    items.append({'empresa':r['empresa'],'tema':r['tema'],'titulo':r['titulo'],'url':r['final_url'],'fonte':re.sub(r'^www\.','',re.sub(r'/.*$','',r['final_url'].split('//')[-1])),'id':f'achado-{len(items)+1:02d}','resumo':summary.get(r['tema'],'Achado curado no radar.'),'impacto':impact.get(r['tema'],'Relevante para monitoramento da ABtec.'),'tipo':'Fonte externa' if 'diariodotransporte' in r['final_url'] or 'technibus' in r['final_url'] or 'antp' in r['final_url'] or 'stgnews' in r['final_url'] else 'Site oficial / produto'})
# trends require real grouped evidence
trend_defs=[
 {'id':'governanca-transparencia-dados','titulo':'Governança de dados e transparência viram pauta institucional da tecnologia de mobilidade','leitura':'A ABtec aparece sustentando dados, tecnologia e transparência como agenda pública. Isso desloca o debate das empresas de tecnologia do papel de fornecedoras para o papel de infraestrutura de governança do transporte.','uso':'Criar pasta ABtec sobre transparência, dados, ENMU, interoperabilidade e indicadores públicos.','themes':['Governança de dados','Transparência / ENMU','Big data / bilhetagem']},
 {'id':'open-payment-bilhetagem-digital','titulo':'Bilhetagem digital e open payment avançam como infraestrutura de relacionamento','leitura':'PIX, Carteira Google, pagamento digital e bilhetagem embarcada aparecem em vários achados. A tendência não é apenas trocar meio de pagamento, mas transformar a bilhetagem em camada de relacionamento e dados.','uso':'Criar pasta sobre open payment brasileiro, Pix, carteiras digitais, validadores e inclusão financeira no transporte.','themes':['PIX no validador','Carteira digital','Bilhetagem digital','Bilhetagem / Lat.Bus']},
 {'id':'apps-plataformas-confianca','titulo':'Apps deixam de ser vitrine e viram plataformas de confiança operacional','leitura':'Cittamobi, Bus2 e SONDA mostram apps/plataformas conectados a tempo real, experiência do usuário, gestão e mobilidade inteligente.','uso':'Criar pasta sobre informação ao passageiro, app como canal público, SLA de dados e integração passageiro-operador-gestor.','themes':['Tempo real / internacionalização','Apps de mobilidade','Smart cities','Mobilidade inteligente']},
 {'id':'ia-dados-gestao','titulo':'IA, dados e sensores entram na narrativa de gestão da mobilidade','leitura':'IA aparece em Prodata/Mais Mobi, big data aparece na Bus2, e reconhecimento facial/monitoramento entram no portfólio das associadas. A tendência pede análise criteriosa para diferenciar caso concreto de discurso genérico.','uso':'Criar pasta sobre IA responsável, analytics, sensores, biometria, privacidade e governança algorítmica.','themes':['IA / gestão','Big data / bilhetagem','Reconhecimento facial','Segurança / tecnologia']},
 {'id':'tecnologia-brasileira-vitrine','titulo':'Tecnologia brasileira de mobilidade busca vitrine nacional e internacional','leitura':'Prodata/Mais Mobi, Bus2, Empresa 1 e SONDA aparecem em eventos, internacionalização e implantação fora de seus mercados tradicionais.','uso':'Criar pasta sobre indústria brasileira de tecnologia para mobilidade, exportação, Lat.Bus, APTA e Paraguai.','themes':['Internacionalização','Tempo real / internacionalização','Apps de mobilidade','Tecnologia / Lat.Bus','Smart cities / mobilidade']},
]
for t in trend_defs:
    t['achados']=[it for it in items if it['tema'] in t['themes']]
trends=[t for t in trend_defs if len(t['achados'])>=2]
by_company={}
for it in items: by_company.setdefault(it['empresa'],[]).append(it)
site={c['nome_oficial']:c['site'] for c in companies}
social_by={}
for s in social: social_by.setdefault(s['empresa'],[]).append(s)
source_groups=[
 ('Instituições e entidades brasileiras','https://www.antp.org.br/','ANTP'),('Instituições e entidades brasileiras','https://www.ntu.org.br/','NTU'),('Instituições e entidades brasileiras','https://www.antptrilhos.org.br/','ANPTrilhos'),('Instituições e entidades brasileiras','https://www.bndes.gov.br/','BNDES'),('Instituições e entidades brasileiras','https://www.gov.br/cidades/pt-br','Ministério das Cidades'),
 ('Pesquisa, smart cities e mobilidade','https://www.wribrasil.org.br/','WRI Brasil'),('Pesquisa, smart cities e mobilidade','https://itdpbrasil.org/','ITDP Brasil'),('Pesquisa, smart cities e mobilidade','https://www.mobilize.org.br/','Mobilize'),('Pesquisa, smart cities e mobilidade','https://portal.connectedsmartcities.com.br/','Connected Smart Cities'),
 ('Imprensa setorial e blogs','https://diariodotransporte.com.br/','Diário do Transporte'),('Imprensa setorial e blogs','https://technibus.com.br/','Technibus'),('Imprensa setorial e blogs','https://viatrolebus.com.br/','Via Trolebus'),('Imprensa setorial e blogs','https://frotacia.com.br/','Frota&Cia'),('Imprensa setorial e blogs','https://www.baguete.com.br/','Baguete')]
css='''
:root{--navy:#10243f;--blue:#1167b1;--cyan:#1ab7c8;--green:#00a884;--amber:#f4a340;--red:#c43d32;--ink:#17212b;--muted:#667787;--line:#dbe7ef;--bg:#f5f8fb;--soft:#fbfdff}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);font-family:Inter,Arial,Helvetica,sans-serif;color:var(--ink);line-height:1.5}.wrap{max-width:1080px;margin:auto;background:#fff;min-height:100vh;padding:24px}.bar{height:10px;background:linear-gradient(90deg,var(--navy),var(--blue),var(--cyan));margin:-24px -24px 24px}.hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.title{font-size:32px;line-height:1;font-weight:950;color:var(--navy);text-transform:uppercase}.subtitle{margin-top:10px;color:var(--muted);font-size:15px}.date{margin-top:8px;font-weight:850}.logo{border:2px solid var(--blue);border-radius:16px;padding:10px 12px;background:#fff;color:var(--blue);font-weight:950;text-align:center}.intro,.summary,.section{border:1px solid var(--line);border-radius:18px;background:var(--soft);padding:16px;margin:16px 0}.jump,.chips,.btnrow{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}.jump a,.chip,.smallbtn{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#fff;color:var(--blue);text-decoration:none;font-weight:850}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card,.trendcard{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:12px 0;break-inside:avoid}.trendcard{border-left:5px solid var(--cyan)}.badge{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:900;background:#e8f4ff;color:var(--blue);border:1px solid #b9d8f2}.badge.trend{background:#e9fbf7;color:#08745f;border-color:#bde9dd}.meta{margin:8px 0;color:var(--muted);font-size:13px;font-weight:750}.card h3,.trendcard h3{margin:8px 0;color:var(--navy);font-size:18px;line-height:1.15}.field{margin:8px 0}.btn{display:inline-block;margin-top:8px;border-radius:999px;padding:9px 13px;background:var(--blue);color:white;font-weight:900;text-decoration:none}.trendbtn{display:inline-block;margin:4px 4px 0 0;border-radius:999px;padding:7px 10px;background:#f1fbfd;border:1px solid #bcecf2;color:#0c6672;text-decoration:none;font-size:13px;font-weight:850}.foot{border-top:1px solid var(--line);margin-top:20px;padding-top:12px;color:var(--muted);font-size:13px}@media(max-width:720px){.wrap{padding:18px}.bar{margin:-18px -18px 20px}.hero{display:block}.title{font-size:27px}.logo{display:inline-block;margin-top:12px}}
'''
def A(h,t,cls=''): return f'<a class="{cls}" href="{esc(h)}" target="_blank" rel="noopener">{esc(t)}</a>' if h.startswith('http') else f'<a class="{cls}" href="{esc(h)}">{esc(t)}</a>'
parts=[f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade — teste analítico {DATE}</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div>']
parts.append('<section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Smart cities e tecnologias aplicadas à mobilidade no Brasil — inteligência semanal para ABtec</div><div class="date">Teste analítico · 10 de outubro de 2026 · janela: últimos 12 meses</div></div><div class="logo">ABtec<br>Mobilidade</div></section>')
parts.append(f'<section class="intro"><strong>Teste editorial com conteúdo vasculhado.</strong> Esta versão usa {len(items)} achados validados com URLs originais, sites oficiais das associadas, redes sociais encontradas nos sites oficiais e fontes setoriais brasileiras. As tendências não são cards automáticos: foram criadas depois da análise dos achados.</section>')
parts.append('<nav class="jump"><a href="#tendencias">Tendências reais encontradas</a><a href="#associadas">Associadas e achados</a><a href="#fontes">Fontes brasileiras para seguir</a><a href="#metodo">Método</a></nav>')
parts.append('<section class="section"><h2>Associadas mapeadas</h2><div class="jump">')
for c in companies:
    name=c['nome_oficial']; count=len(by_company.get(name,[])); label=f'{name} ({count})' if count else f'{name} (site/redes)'
    parts.append(A('#assoc-'+slug(name),label))
parts.append('</div><p class="meta">Botões levam ao bloco da associada. Dentro de cada bloco há site oficial, redes encontradas e matérias/achados quando houver.</p></section>')
parts.append('<section class="section" id="tendencias"><h2>Tendências reais encontradas</h2><p>As tendências abaixo só aparecem porque há pelo menos dois achados sustentando a leitura. Os botões levam às fontes específicas.</p>')
for t in trends:
    parts.append(f'<article class="trendcard" id="trend-{t["id"]}"><span class="badge trend">Tendência validada</span><h3>{esc(t["titulo"])}</h3><div class="field"><b>Leitura executiva:</b> {esc(t["leitura"])}</div><div class="field"><b>Como a ABtec pode usar:</b> {esc(t["uso"])}</div><div class="field"><b>Achados que sustentam:</b><br>')
    for it in t['achados']: parts.append(f'<a class="trendbtn" href="#achado-{esc(it["id"])}">{esc(it["empresa"])} · {esc(it["tema"])}</a>')
    parts.append('</div></article>')
parts.append('</section>')
parts.append('<section class="summary"><h2>Resumo executivo</h2><ul><li>A agenda mais forte é a combinação entre governança de dados, transparência e bilhetagem como infraestrutura de informação pública.</li><li>Open payment, Pix, carteiras digitais e bilhetagem digital aparecem como frente concreta para associadas.</li><li>Apps e plataformas deixam de ser apenas canal de informação e passam a compor gestão, confiança operacional e relacionamento com usuário.</li><li>Há oportunidade clara para a ABtec organizar pastas por tema, e não por empresa: dados/transparência, pagamentos, apps, IA/sensores e internacionalização.</li></ul></section>')
parts.append('<section class="section" id="associadas"><h2>Achados por associada</h2>')
for c in companies:
    name=c['nome_oficial']; parts.append(f'<section id="assoc-{slug(name)}"><h3>{esc(name)}</h3><div class="btnrow">{A(c["site"],"Site oficial","smallbtn")}')
    for s in social_by.get(name,[])[:5]: parts.append(A(s['url'],s['plataforma'].replace('www.',''),'smallbtn'))
    for t in trends:
        if any(it['empresa']==name for it in t['achados']): parts.append(A('#trend-'+t['id'],'Tendência: '+t['titulo'][:38],'smallbtn'))
    parts.append('</div>')
    if name in by_company:
        for it in by_company[name]:
            parts.append(f'<article class="card" id="achado-{esc(it["id"])}"><span class="badge">{esc(it["tipo"])}</span><div class="meta">{esc(it["empresa"])} | {esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3><div class="field"><b>Resumo:</b> {esc(it["resumo"])}</div><div class="field"><b>Por que importa:</b> {esc(it["impacto"])}</div>{A(it["url"],"Abrir fonte","btn")}</article>')
    else:
        parts.append('<article class="card"><span class="badge">Monitoramento</span><h3>Sem achado externo curado nesta prévia</h3><div class="field">Empresa mapeada por site oficial e redes; entra na próxima rodada de imprensa e redes sociais.</div></article>')
    parts.append('</section>')
parts.append('</section>')
parts.append('<section class="section" id="fontes"><h2>Fontes brasileiras para seguir</h2><p>Base inicial inspirada no raciocínio do PANORAMA/UITP, adaptada ao tema ABtec: tecnologia, transporte público, mobilidade urbana e smart cities no Brasil.</p><div class="grid">')
for group in ['Instituições e entidades brasileiras','Pesquisa, smart cities e mobilidade','Imprensa setorial e blogs']:
    parts.append(f'<article class="card"><h3>{group}</h3><div class="btnrow">')
    for g,u,n in source_groups:
        if g==group: parts.append(A(u,n,'smallbtn'))
    parts.append('</div></article>')
parts.append('</div></section>')
parts.append('<section class="section" id="metodo"><h2>Método e próximos passos</h2><ul><li>Janela máxima aplicada: 12 meses, de 2025-10-10 a 2026-10-10.</li><li>Camadas consultadas: site ABtec, sites oficiais das associadas, redes sociais encontradas nos sites oficiais, Google News/portais setoriais e fontes brasileiras de mobilidade/smart cities.</li><li>Próxima melhoria: leitura manual de posts recentes de LinkedIn/Instagram/YouTube das associadas e criação de pastas temáticas persistentes para a ABtec.</li><li>Itens antigos fora da janela de um ano foram removidos do protótipo.</li></ul></section>')
parts.append('<footer class="foot"><p><strong>Nota:</strong> protótipo público de teste. Antes de uso institucional, recomenda-se validação final de tom, prioridade e sensibilidade comercial com a ABtec.</p></footer></main></body></html>')
html_out=''.join(parts)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'selecionados_curados.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),'utf-8')
(OUT/'tendencias.json').write_text(json.dumps(trends,ensure_ascii=False,indent=2),'utf-8')
(OUT/'index.html').write_text(html_out,'utf-8')
(ROOT/'prototipos/layout-semanal/index.html').write_text(html_out,'utf-8')
home=f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div><section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Inteligência semanal sobre smart cities e tecnologia para mobilidade no Brasil</div><div class="date">Página inicial pública de teste</div></div><div class="logo">ABtec<br>Mobilidade</div></section><section class="intro"><p>Ambiente separado do PANORAMA para organizar achados, tendências e pastas estratégicas para a ABtec Mobilidade.</p><div class="btnrow"><a class="btn" href="edicoes-semanais/{DATE}/">Abrir teste analítico</a><a class="smallbtn" href="prototipos/layout-semanal/">Abrir protótipo de layout</a><a class="smallbtn" href="fontes/associadas_abtec_oficial.csv">Base de associadas</a></div></section></main></body></html>'
(ROOT/'index.html').write_text(home,'utf-8')
print(json.dumps({'items':len(items),'trends':len(trends),'companies':len(companies),'cards':html_out.count('class="card"'),'google_news':html_out.count('news.google.com'),'empty_href':html_out.count('href="#"')},ensure_ascii=False,indent=2))
