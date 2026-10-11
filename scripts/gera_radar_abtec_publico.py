#!/usr/bin/env python3
from pathlib import Path
import csv,json,html,re
ROOT=Path('/opt/data/abtec_mobilidade_inteligencia')
DATE='2026-10-10'
OUT=ROOT/'edicoes-semanais'/DATE
qa=json.loads((ROOT/'buscas'/'qa_urls_curadoria_manual_2026-10-10.json').read_text('utf-8'))
companies=list(csv.DictReader((ROOT/'fontes'/'associadas_abtec_oficial.csv').open(encoding='utf-8')))
social=json.loads((ROOT/'buscas'/f'sociais_associadas_{DATE}.json').read_text('utf-8'))

def esc(s): return html.escape(str(s or ''),quote=True)
def slug(s):
    s=str(s).lower()
    for a,b in {'á':'a','à':'a','ã':'a','â':'a','é':'e','ê':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u','ç':'c'}.items(): s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','-',s).strip('-') or 'item'
def A(h,t,cls=''):
    target='_blank' if h.startswith('http') else '_self'
    return f'<a class="{cls}" href="{esc(h)}" target="{target}" rel="noopener">{esc(t)}</a>'
summary={
 'Governança de dados':'A ABtec conecta tecnologia, governança de dados e transparência como agenda pública do transporte coletivo.',
 'Transparência / ENMU':'A cobertura usa o ENMU como gancho para defender tecnologia na qualificação da gestão e da informação pública.',
 'Tempo real / internacionalização':'A Bus2 aparece aplicada fora do Brasil com monitoramento em tempo real de ônibus.',
 'Apps de mobilidade':'A presença da Bus2 no Paraguai reforça exportação de solução brasileira para apps de mobilidade.',
 'Big data / bilhetagem':'A bilhetagem aparece como camada de leitura inteligente da operação de ônibus.',
 'Smart cities':'O CittaMobi apareceu como solução tecnológica para cidades inteligentes em mobilidade urbana, mas ficará em ecossistema até validação societária/associativa com Cittati.',
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
impact={k:v for k,v in {
 'Governança de dados':'Sustenta uma pasta de transparência, dados públicos, interoperabilidade e accountability.',
 'Transparência / ENMU':'Ajuda a ABtec a se posicionar como voz técnica em maturidade digital do setor.',
 'Tempo real / internacionalização':'Mostra tecnologia brasileira com potencial de exportação regional e impacto no usuário.',
 'Apps de mobilidade':'Reforça apps como camada de confiança, previsibilidade e informação ao passageiro.',
 'Big data / bilhetagem':'Indica que bilhetagem está virando sensor urbano, não só mecanismo de cobrança.',
 'Smart cities':'Entra como achado de ecossistema, não como achado de associada, até validação da relação CittaMobi/Cittati.',
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
 'Carteira digital':'Carteiras digitais ampliam meios de pagamento e aproximam transporte de ecossistemas financeiros.'}.items()}
items=[]
for r in qa:
    if r['status']!='ok': continue
    empresa=r['empresa']
    tipo='Fonte externa' if any(x in r['final_url'] for x in ['diariodotransporte','technibus','antp','stgnews']) else 'Site oficial / produto'
    if empresa=='Cittati' and r['tema']=='Smart cities':
        empresa='Ecossistema Smart Cities'
        tipo='Ecossistema / requer validação'
    items.append({'empresa':empresa,'tema':r['tema'],'titulo':r['titulo'],'url':r['final_url'],'fonte':re.sub(r'^www\.','',re.sub(r'/.*$','',r['final_url'].split('//')[-1])),'id':f'achado-{len(items)+1:02d}','resumo':summary.get(r['tema'],'Achado curado no radar.'),'impacto':impact.get(r['tema'],'Relevante para monitoramento da ABtec.'),'tipo':tipo})
# clusters, not trends
cluster_defs=[
 {'id':'apps-plataformas-confianca','titulo':'Apps, plataformas e informação ao passageiro','leitura':'Achados ligados a apps, tempo real e plataformas digitais indicam que a comunicação com o usuário é parte da infraestrutura tecnológica do transporte.', 'pasta':'Pasta sugerida: informação ao passageiro, app como canal público, SLA de dados e integração passageiro-operador-gestor.', 'themes':['Tempo real / internacionalização','Apps de mobilidade','Smart cities','Mobilidade inteligente']},
 {'id':'bilhetagem-open-payment','titulo':'Bilhetagem digital, Pix e carteiras digitais','leitura':'Pix no validador, Carteira Google, dispositivos embarcados e bilhetagem digital aparecem como frente recorrente do setor.', 'pasta':'Pasta sugerida: open payment brasileiro, validadores, carteiras digitais, inclusão financeira e dados de pagamento.', 'themes':['PIX no validador','Carteira digital','Bilhetagem digital','Bilhetagem / Lat.Bus']},
 {'id':'dados-transparencia-governanca','titulo':'Dados, transparência e governança pública','leitura':'ABtec, ENMU e big data de bilhetagem aparecem como insumos para qualificar gestão pública, indicadores e transparência.', 'pasta':'Pasta sugerida: dados públicos, interoperabilidade, transparência, ENMU e indicadores para transporte coletivo.', 'themes':['Governança de dados','Transparência / ENMU','Big data / bilhetagem']},
 {'id':'ia-sensores-seguranca','titulo':'IA, sensores, biometria e segurança operacional','leitura':'IA, reconhecimento facial, segurança e analytics surgem como assuntos de alto potencial, mas exigem critério para separar aplicação real de discurso comercial.', 'pasta':'Pasta sugerida: IA responsável, sensores, biometria, privacidade, segurança e governança algorítmica.', 'themes':['IA / gestão','Big data / bilhetagem','Reconhecimento facial','Segurança / tecnologia']},
 {'id':'internacionalizacao-vitrines','titulo':'Internacionalização, eventos e vitrine de tecnologia brasileira','leitura':'Eventos, Lat.Bus, APTA e casos fora do Brasil mostram oportunidades de posicionar tecnologia nacional de mobilidade como pauta setorial.', 'pasta':'Pasta sugerida: exportação, feiras, casos internacionais, presença LATAM e agenda institucional das associadas.', 'themes':['Internacionalização','Tempo real / internacionalização','Apps de mobilidade','Tecnologia / Lat.Bus','Smart cities / mobilidade']},
 {'id':'integracao-sistemas','titulo':'Integração de sistemas e gestão operacional','leitura':'Integração, sistemas embarcados e gestão de operação aparecem como base menos visível, mas crítica, para cidades inteligentes e transporte público digital.', 'pasta':'Pasta sugerida: ITS, backoffice, integração operacional, gestão de frota e plataformas de controle.', 'themes':['Integração de sistemas','Sistema integrado','Bilhetagem digital','Mobilidade inteligente']},
]
for c in cluster_defs:
    c['achados']=[it for it in items if it['tema'] in c['themes']]
clusters=sorted([c for c in cluster_defs if c['achados']], key=lambda x:x['titulo'])
by_company={}
ecosystem=[]
for it in items:
    if it['empresa']=='Ecossistema Smart Cities': ecosystem.append(it)
    else: by_company.setdefault(it['empresa'],[]).append(it)
social_by={}
for s in social: social_by.setdefault(s['empresa'],[]).append(s)
source_groups=[('Instituições e entidades brasileiras','https://www.antp.org.br/','ANTP'),('Instituições e entidades brasileiras','https://www.ntu.org.br/','NTU'),('Instituições e entidades brasileiras','https://www.antptrilhos.org.br/','ANPTrilhos'),('Instituições e entidades brasileiras','https://www.bndes.gov.br/','BNDES'),('Instituições e entidades brasileiras','https://www.gov.br/cidades/pt-br','Ministério das Cidades'),('Pesquisa, smart cities e mobilidade','https://www.wribrasil.org.br/','WRI Brasil'),('Pesquisa, smart cities e mobilidade','https://itdpbrasil.org/','ITDP Brasil'),('Pesquisa, smart cities e mobilidade','https://www.mobilize.org.br/','Mobilize'),('Pesquisa, smart cities e mobilidade','https://portal.connectedsmartcities.com.br/','Connected Smart Cities'),('Imprensa setorial e blogs','https://diariodotransporte.com.br/','Diário do Transporte'),('Imprensa setorial e blogs','https://technibus.com.br/','Technibus'),('Imprensa setorial e blogs','https://viatrolebus.com.br/','Via Trolebus'),('Imprensa setorial e blogs','https://frotacia.com.br/','Frota&Cia'),('Imprensa setorial e blogs','https://www.baguete.com.br/','Baguete')]
css='''
:root{--navy:#10243f;--blue:#1167b1;--cyan:#1ab7c8;--green:#00a884;--amber:#f4a340;--red:#c43d32;--ink:#17212b;--muted:#667787;--line:#dbe7ef;--bg:#f5f8fb;--soft:#fbfdff}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);font-family:Inter,Arial,Helvetica,sans-serif;color:var(--ink);line-height:1.5}.wrap{max-width:1080px;margin:auto;background:#fff;min-height:100vh;padding:24px}.bar{height:10px;background:linear-gradient(90deg,var(--navy),var(--blue),var(--cyan));margin:-24px -24px 24px}.hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.title{font-size:32px;line-height:1;font-weight:950;color:var(--navy);text-transform:uppercase}.subtitle{margin-top:10px;color:var(--muted);font-size:15px}.date{margin-top:8px;font-weight:850}.logo{border:2px solid var(--blue);border-radius:16px;padding:10px 12px;background:#fff;color:var(--blue);font-weight:950;text-align:center}.intro,.summary,.section{border:1px solid var(--line);border-radius:18px;background:var(--soft);padding:16px;margin:16px 0}.jump,.btnrow{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}.jump a,.smallbtn{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#fff;color:var(--blue);text-decoration:none;font-weight:850}.cluster-select{width:100%;max-width:620px;border:1px solid var(--line);border-radius:14px;padding:11px 12px;background:#fff;color:var(--navy);font-weight:850;font-size:15px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card,.clustercard{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:12px 0;break-inside:avoid}.clustercard{border-left:7px solid var(--cyan);box-shadow:0 2px 8px rgba(16,36,63,.05)}.badge{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:900;background:#e8f4ff;color:var(--blue);border:1px solid #b9d8f2}.badge.cluster{background:#e9fbf7;color:#08745f;border-color:#bde9dd}.meta{margin:8px 0;color:var(--muted);font-size:13px;font-weight:750}.card h3{margin:8px 0;color:var(--navy);font-size:18px;line-height:1.15}.clustercard h3{margin:8px 0 10px;color:var(--navy);font-size:24px;line-height:1.08;border-bottom:1px solid var(--line);padding-bottom:8px}.field{margin:8px 0}.btn{display:inline-block;margin-top:8px;border-radius:999px;padding:9px 13px;background:var(--blue);color:white;font-weight:900;text-decoration:none}.itemlink{display:inline-block;margin:4px 4px 0 0;border-radius:999px;padding:7px 10px;background:#f1fbfd;border:1px solid #bcecf2;color:#0c6672;text-decoration:none;font-size:13px;font-weight:850}.criteria{background:#fff7e9;border-color:#f5d59f}.foot{border-top:1px solid var(--line);margin-top:20px;padding-top:12px;color:var(--muted);font-size:13px}@media(max-width:720px){.wrap{padding:18px}.bar{margin:-18px -18px 20px}.hero{display:block}.title{font-size:27px}.logo{display:inline-block;margin-top:12px}.clustercard h3{font-size:21px}}
'''
parts=[f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade — clusters temáticos {DATE}</title><style>{css}</style><script>function goCluster(sel){{if(sel.value) location.hash=sel.value; sel.selectedIndex=0;}}</script></head><body><main class="wrap"><div class="bar"></div>']
parts.append('<section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Smart cities e tecnologias aplicadas à mobilidade no Brasil — inteligência semanal para ABtec</div><div class="date">Teste analítico · 10 de outubro de 2026 · janela: últimos 12 meses</div></div><div class="logo">ABtec<br>Mobilidade</div></section>')
parts.append(f'<section class="intro"><strong>Teste editorial com conteúdo vasculhado.</strong> Esta versão usa {len(items)} achados validados com URLs originais, sites oficiais das associadas, redes sociais encontradas nos sites oficiais e fontes setoriais brasileiras. A seção principal agora é de <b>clusters temáticos</b>, não de tendências: tendência será uma conclusão posterior, com critérios.</section>')
parts.append('<nav class="jump"><a href="#clusters">Clusters temáticos</a><a href="#associadas">Associadas e canais</a><a href="#ecossistema">Ecossistema fora das associadas</a><a href="#criterios">Critérios futuros de tendência</a><a href="#fontes">Fontes brasileiras</a></nav>')
parts.append('<section class="section"><h2>Escolha um cluster temático</h2><select class="cluster-select" onchange="goCluster(this)"><option value="">Abrir lista de temas em ordem alfabética</option>')
for c in clusters: parts.append(f'<option value="cluster-{c["id"]}">{esc(c["titulo"])}</option>')
parts.append('</select><p class="meta">Os clusters organizam assuntos recorrentes. Eles ainda não são chamados de tendência.</p></section>')
parts.append('<section class="section"><h2>Associadas mapeadas</h2><div class="jump">')
for c in companies:
    name=c['nome_oficial']; count=len(by_company.get(name,[])); label=f'{name} ({count})' if count else f'{name} (canais)'
    parts.append(A('#assoc-'+slug(name),label))
parts.append('</div><p class="meta">Nos blocos das associadas ficam somente site oficial, canais de comunicação e achados da própria associada. Sem botões de cluster aqui.</p></section>')
parts.append('<section class="section" id="clusters"><h2>Clusters temáticos encontrados</h2><p>Clusters são pastas de assunto. Eles ajudam a acumular evidências para, no futuro, identificar tendências de mercado com critérios.</p>')
for c in clusters:
    parts.append(f'<article class="clustercard" id="cluster-{c["id"]}"><span class="badge cluster">Cluster temático</span><h3>{esc(c["titulo"])}</h3><div class="field"><b>Leitura inicial:</b> {esc(c["leitura"])}</div><div class="field"><b>Uso possível para a ABtec:</b> {esc(c["pasta"])}</div><div class="field"><b>Achados relacionados:</b><br>')
    for it in sorted(c['achados'], key=lambda x:(x['empresa'],x['tema'])): parts.append(f'<a class="itemlink" href="#achado-{esc(it["id"])}">{esc(it["empresa"])} · {esc(it["tema"])}</a>')
    parts.append('</div></article>')
parts.append('</section>')
parts.append('<section class="section criteria" id="criterios"><h2>Quando um cluster vira tendência?</h2><p>Proposta de critérios para validarmos juntas antes de usar a palavra tendência:</p><ul><li><b>Recorrência:</b> aparece em pelo menos 3 fontes ou 3 associadas em janela recente.</li><li><b>Persistência:</b> reaparece por 2 ou mais semanas/meses, não é um caso isolado.</li><li><b>Impacto setorial:</b> muda regulação, operação, financiamento, experiência do usuário ou modelo de negócio.</li><li><b>Adoção verificável:</b> há implantação, contrato, produto, evento técnico ou case real — não só discurso.</li><li><b>Relevância para ABtec:</b> ajuda a associação a criar pauta, pasta, posicionamento ou agenda institucional.</li></ul></section>')
parts.append('<section class="summary"><h2>Resumo executivo</h2><ul><li>O material atual é melhor lido como mapa de clusters: dados/transparência, bilhetagem/open payment, apps/plataformas, IA/sensores, integração e internacionalização.</li><li>As redes sociais entram como canais de comunicação das associadas, não como prova automática de tendência.</li><li>CittaMobi foi retirado do bloco Cittati e movido para ecossistema Smart Cities até validação formal da relação.</li><li>O próximo passo é acumular achados por cluster ao longo das semanas para identificar o que realmente vira tendência.</li></ul></section>')
parts.append('<section class="section" id="associadas"><h2>Associadas: canais e achados</h2>')
for c in companies:
    name=c['nome_oficial']; parts.append(f'<section id="assoc-{slug(name)}"><h3>{esc(name)}</h3><div class="btnrow">{A(c["site"],"Site oficial","smallbtn")}')
    for s in social_by.get(name,[])[:8]:
        label=s.get('label') or s.get('plataforma','Canal').replace('www.','').replace('.com','').title()
        parts.append(A(s['url'],label,'smallbtn'))
    parts.append('</div>')
    if name in by_company:
        for it in by_company[name]:
            parts.append(f'<article class="card" id="achado-{esc(it["id"])}"><span class="badge">{esc(it["tipo"])}</span><div class="meta">{esc(it["empresa"])} | {esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3><div class="field"><b>Resumo:</b> {esc(it["resumo"])}</div><div class="field"><b>Por que importa:</b> {esc(it["impacto"])}</div>{A(it["url"],"Abrir fonte","btn")}</article>')
    else:
        parts.append('<article class="card"><span class="badge">Monitoramento</span><h3>Sem achado externo curado nesta prévia</h3><div class="field">Empresa mapeada por site oficial e canais. Entra na próxima rodada de imprensa, blogs e redes sociais.</div></article>')
    parts.append('</section>')
parts.append('</section>')
parts.append('<section class="section" id="ecossistema"><h2>Ecossistema fora das associadas / requer validação</h2><p>Achados úteis para o radar, mas que não devem ser atribuídos a uma associada sem confirmação.</p>')
for it in ecosystem:
    parts.append(f'<article class="card" id="achado-{esc(it["id"])}"><span class="badge">{esc(it["tipo"])}</span><div class="meta">{esc(it["fonte"])} | {esc(it["tema"])}</div><h3>{esc(it["titulo"])}</h3><div class="field"><b>Resumo:</b> {esc(it["resumo"])}</div><div class="field"><b>Observação editorial:</b> {esc(it["impacto"])}</div>{A(it["url"],"Abrir fonte","btn")}</article>')
parts.append('</section>')
parts.append('<section class="section" id="fontes"><h2>Fontes brasileiras para seguir</h2><div class="grid">')
for group in ['Imprensa setorial e blogs','Instituições e entidades brasileiras','Pesquisa, smart cities e mobilidade']:
    parts.append(f'<article class="card"><h3>{group}</h3><div class="btnrow">')
    for g,u,n in source_groups:
        if g==group: parts.append(A(u,n,'smallbtn'))
    parts.append('</div></article>')
parts.append('</div></section>')
parts.append('<section class="section"><h2>Método</h2><ul><li>Janela máxima: 12 meses, de 2025-10-10 a 2026-10-10.</li><li>Camadas consultadas: site ABtec, sites oficiais das associadas, canais sociais encontrados nos sites oficiais, imprensa setorial, blogs de tecnologia/mobilidade e fontes brasileiras de smart cities.</li><li>Redes sociais aparecem como canais oficiais; análise de posts recentes será a próxima camada.</li></ul></section>')
parts.append('<footer class="foot"><p><strong>Nota:</strong> protótipo público de teste. Antes de uso institucional, recomenda-se validação final de tom, prioridade e sensibilidade comercial com a ABtec.</p></footer></main></body></html>')
html_out=''.join(parts)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'selecionados_curados.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),'utf-8')
(OUT/'clusters_tematicos.json').write_text(json.dumps(clusters,ensure_ascii=False,indent=2),'utf-8')
(OUT/'index.html').write_text(html_out,'utf-8')
(ROOT/'prototipos/layout-semanal/index.html').write_text(html_out,'utf-8')
home=f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Radar ABtec Mobilidade</title><style>{css}</style></head><body><main class="wrap"><div class="bar"></div><section class="hero"><div><div class="title">Radar ABtec Mobilidade</div><div class="subtitle">Inteligência semanal sobre smart cities e tecnologia para mobilidade no Brasil</div><div class="date">Página inicial pública de teste</div></div><div class="logo">ABtec<br>Mobilidade</div></section><section class="intro"><p>Ambiente separado do PANORAMA para organizar achados, clusters temáticos e futuras tendências para a ABtec Mobilidade.</p><div class="btnrow"><a class="btn" href="edicoes-semanais/{DATE}/">Abrir teste analítico</a><a class="smallbtn" href="prototipos/layout-semanal/">Abrir protótipo de layout</a><a class="smallbtn" href="fontes/associadas_abtec_oficial.csv">Base de associadas</a></div></section></main></body></html>'
(ROOT/'index.html').write_text(home,'utf-8')
print(json.dumps({'items':len(items),'clusters':len(clusters),'ecosystem':len(ecosystem),'companies':len(companies),'cards':html_out.count('class="card"'),'cluster_cards':html_out.count('Cluster temático'),'tendencia_word':html_out.lower().count('tendência'),'google_news':html_out.count('news.google.com'),'empty_href':html_out.count('href="#"')},ensure_ascii=False,indent=2))
