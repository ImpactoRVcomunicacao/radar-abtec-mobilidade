#!/usr/bin/env python3
from pathlib import Path
import json,re,html,urllib.request,urllib.parse
ROOT=Path('/opt/data/abtec_mobilidade_inteligencia')
DATE='2026-10-10'
items=json.loads((ROOT/'edicoes-semanais'/DATE/'selecionados_preliminares.json').read_text('utf-8'))
HEAD={'User-Agent':'Mozilla/5.0 Radar ABtec link resolver'}
SOURCES=['https://diariodotransporte.com.br/','https://technibus.com.br/','https://viatrolebus.com.br/','https://www.mobilize.org.br/noticias/','https://www.frotacia.com.br/']

def norm(s): return re.sub(r'\W+',' ',html.unescape(s).lower()).strip()
def fetch(url):
    try: return urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=25).read().decode('utf-8','ignore')
    except Exception: return ''
def links_from(url, data):
    out=[]
    for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',data,re.I):
        href=urllib.parse.urljoin(url,html.unescape(m.group(1)))
        label=html.unescape(re.sub(r'\s+',' ',re.sub('<.*?>',' ',m.group(2))).strip())
        if len(label)>20: out.append((label,href))
    return out
all_links=[]
for src in SOURCES:
    data=fetch(src)
    all_links += links_from(src,data)
# add current site direct category pages maybe already enough
manual={
 'Aplicativo BuzzPY com tecnologia da brasileira Bus2 estreia no Paraguai':'https://diariodotransporte.com.br/2026/10/09/aplicativo-buzzpy-com-tecnologia-da-brasileira-bus2-estreia-no-paraguai-com-monitoramento-em-tempo-real-de-onibus/',
 'Empresa 1 apresenta tecnologias de bilhetagem digital e mobilidade urbana na LAT.BUS 2026':'https://www.frotacia.com.br/empresa-1-apresenta-tecnologias-de-bilhetagem-digital-e-mobilidade-urbana-na-lat-bus-2026/',
 'ABTEC defende tecnologia e governança de dados como pilares':'https://technibus.com.br/2026/10/06/abtec-defende-tecnologia-e-governanca-de-dados-como-pilares-para-ampliar-a-transparencia-do-transporte-publico',
 'Após Estudo Nacional de Mobilidade Urbana apontar falhas na transparência':'https://diariodotransporte.com.br/2026/10/04/apos-estudo-nacional-de-mobilidade-urbana-apontar-falhas-na-transparencia-abtec-defende-uso-de-tecnologia-para-qualificar-transporte-publico/',
 'Prefeitura de Jundiaí (SP) testa nova tecnologia de monitoramento nos ônibus':'https://diariodotransporte.com.br/2026/10/08/prefeitura-de-jundiai-sp-testa-nova-tecnologia-de-monitoramento-nos-onibus-para-otimizar-a-gestao-da-frota/',
 'IPT disponibiliza parecer técnico sobre aplicativo Cittamobi':'https://diariodotransporte.com.br/2026/10/05/ipt-disponibiliza-parecer-tecnico-sobre-aplicativo-cittamobi-como-solucao-tecnologica-para-cidades-inteligentes-em-mobilidade-urbana/',
 'Empresa 1, pioneira da bilhetagem digital':'https://diariodotransporte.com.br/2026/10/09/empresa-1-pioneira-da-bilhetagem-digital-no-transporte-publico-brasileiro-anuncia-marcos-maciel-como-novo-ceo/',
 'Empresa 1 cria campanha “Moderniza!”':'https://diariodotransporte.com.br/2026/10/07/empresa-1-cria-campanha-moderniza-para-ajudar-empresarios-de-onibus-a-atualizar-as-tecnologias-de-suas-frotas/',
 'Prodata Mais Mobi leva tecnologia brasileira ao maior evento de transporte público dos EUA':'https://diariodotransporte.com.br/2026/10/08/prodata-mais-mobi-leva-tecnologia-brasileira-ao-maior-evento-de-transporte-publico-dos-eua/',
 'Prodata Mobility participa do Fórum Mineiro de Mobilidade Urbana':'https://diariodotransporte.com.br/2026/10/06/prodata-mobility-participa-do-forum-mineiro-de-mobilidade-urbana-e-destaca-solucoes-tecnologicas-para-o-transporte-publico/',
 'Prodata Mobility Brasil inova mais uma vez e oferece experiência integrada':'https://diariodotransporte.com.br/2026/10/03/prodata-mobility-brasil-inova-mais-uma-vez-e-oferece-experiencia-integrada-nos-modais-de-pagamento-digital-de-onibus-e-vlts-na-baixada-santista/',
 'Sonda apresenta tecnologias para transformar transporte e mobilidade urbana':'https://technibus.com.br/2026/08/13/sonda-apresenta-tecnologias-para-transformar-transporte-e-mobilidade-urbana-durante-a-lat-bus2026',
 'Pagamento de tarifas de transporte público via QR Code':'https://diariodotransporte.com.br/2026/10/06/pagamento-de-tarifas-de-transporte-publico-via-qr-code-sonda-e-pioneira-no-modelo-e-acumula-mais-de-15-milhao-de-usuarios-do-sistema-na-america-latina/',
 'Metrô do DF, em parceria com Transdata e Mastercard':'https://diariodotransporte.com.br/2026/10/07/metro-do-df-em-parceria-com-transdata-e-mastercard-passa-a-aceitar-cartoes-de-debito-e-credito-por-aproximacao/',
 'Tecnologia e integração de sistemas redefinem o futuro do transporte público':'https://technibus.com.br/2026/09/24/tecnologia-e-integracao-de-sistemas-redefinem-o-futuro-do-transporte-publico-aponta-romano-garcia-da-transdata',
 'Lançado o primeiro app de mobilidade do Paraguai com tecnologia Bus2':'https://technibus.com.br/2026/10/09/lancado-o-primeiro-app-de-mobilidade-do-paraguai-com-tecnologia-bus2',
 'João Ronco Júnior, presidente da Prodata Mobility Brasil':'https://technibus.com.br/2026/09/25/joao-ronco-junior-presidente-da-prodata-mobility-brasil-a-bilhetagem-eletronica-no-brasil-tem-evoluido-com-foco-em-inovacao-e-eficiencia',
}
resolved=[]
for it in items:
    title=it['title']
    found=None
    for k,u in manual.items():
        if norm(k)[:45] in norm(title) or norm(title)[:45] in norm(k):
            found=u; break
    if not found:
        nt=norm(title)
        best=None; bestscore=0
        words=set(nt.split())
        for label,href in all_links:
            if any(d in href for d in ['diariodotransporte','technibus','frotacia','viatrolebus','mobilize']):
                score=len(words & set(norm(label).split()))
                if score>bestscore:
                    bestscore=score; best=(label,href)
        if bestscore>=5: found=best[1]
    if found:
        it['url']=found
        resolved.append(it)
# keep only resolved original links
(ROOT/'edicoes-semanais'/DATE/'selecionados_preliminares_resolvidos.json').write_text(json.dumps(resolved,ensure_ascii=False,indent=2),encoding='utf-8')
# patch html buttons to original or remove card if unresolved not easy: regenerate by editing known links and hide unresolved cards? simple replace URLs in html for resolved titles
html_path=ROOT/'edicoes-semanais'/DATE/'index.html'
s=html_path.read_text('utf-8')
for it in resolved:
    # replace first google url after title occurrence
    pos=s.find(html.escape(it['title']))
    if pos!=-1:
        href_pos=s.find('href="https://news.google.com',pos)
        if href_pos!=-1:
            end=s.find('"',href_pos+6)
            s=s[:href_pos+6]+html.escape(it['url'])+s[end:]
# mark unresolved warning at intro
s=s.replace('achados de imprensa/setor selecionados para revisão humana.', f'achados brutos; {len(resolved)} com links originais resolvidos para esta prévia. Itens restantes exigem revisão manual.')
html_path.write_text(s,'utf-8')
print({'resolved':len(resolved),'remaining_gnews':s.count('news.google.com')})
for it in resolved[:20]: print('-',it['title'],'=>',it['url'])
