#!/usr/bin/env python3
"""Archive the validated daily incremental ABtec Radar scan for 2026-10-23.
No public page or weekly edition is modified.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path('/opt/data/abtec_mobilidade_inteligencia')
OUT = ROOT / 'buscas'
RUN_DATE = '2026-10-23'
WINDOW_START = '2026-10-22'

probe = json.loads((OUT / f'prova_fontes_radar_abtec_{RUN_DATE}.json').read_text(encoding='utf-8'))
checked = probe['sources_checked']

curated = [{
    'id': '2026-10-23-01',
    'cluster': 'Bilhetagem digital e dados regulatórios',
    'maturity': 'assunto monitorado',
    'title': 'Bilhetagem digital passa a integrar o Monitriip na plataforma da ONBOARD',
    'source': 'Diário do Transporte',
    'published_date': '2026-10-22',
    'url': 'https://diariodotransporte.com.br/2026/10/22/bilhetagem-digital-passa-a-integrar-o-monitriip-na-plataforma-da-onboard/',
    'summary': 'A ONBOARD anunciou a integração de sua plataforma de bilhetagem digital ao Monitriip, sistema da ANTT voltado ao monitoramento do transporte rodoviário interestadual e internacional de passageiros.',
    'why_it_matters': 'É o achado incremental mais aderente à agenda ABtec: aproxima bilhetagem digital e dados operacionais de uma infraestrutura regulatória federal. Ainda é um sinal de integração; a fonte consultada não detalha escopo contratual, cronograma, operadores atendidos ou indicadores de adoção.',
    'associates': ['ONBOARD'],
    'link_status': 'aberto_validado',
    'citation': 1,
}]

discarded = [
    {
        'title': 'Linhas Paulistar terão guias de turismo em circuitos gratuitos de ônibus elétricos em São Paulo',
        'source': 'Diário do Transporte',
        'url': 'https://diariodotransporte.com.br/2026/10/23/linhas-paulistar-terao-guias-de-turismo-nos-ultimos-domingos-de-outubro-novembro-e-dezembro-confira-horarios-trajetos-e-atracoes-dos-cinco-circuitos-gratuitos-de-onibus-eletricos-em-sao-paulo/',
        'reason': 'ação turística e operacional; não traz componente de tecnologia embarcada, dados ou inovação setorial verificável.',
    },
    {
        'title': 'Linha 11-Coral tem problemas e trens operam com restrições',
        'source': 'Diário do Transporte',
        'url': 'https://diariodotransporte.com.br/2026/10/23/linha-11-coral-tem-problemas-e-trens-operam-com-restricoes-nesta-sexta-feira-23/',
        'reason': 'ocorrência operacional pontual sem evidência de falha sistêmica ou camada tecnológica a analisar nesta leitura.',
    },
    {
        'title': 'Artesp renova registro da Next Mobilidade por mais um ano',
        'source': 'Diário do Transporte',
        'url': 'https://diariodotransporte.com.br/2026/10/23/artesp-renova-registro-da-next-mobilidade-por-mais-um-ano-em-meio-a-processo-que-pode-encerrar-concessao-do-brt-abc-e-dos-onibus-metropolitanos/',
        'reason': 'ato administrativo de concessão sem especificação de ITS, bilhetagem, dados ou tecnologia associada.',
    },
    {
        'title': '“O momento é de incerteza”, avalia Walter Barbosa da Mercedes-Benz',
        'source': 'Technibus',
        'url': 'https://technibus.com.br/2026/10/23/o-momento-e-de-incerteza-avalia-walter-barbosa-da-mercedes-benz',
        'reason': 'leitura de mercado industrial sem anúncio verificável ligado a soluções ABtec, ITS, pagamentos ou digitalização operacional.',
    },
    {
        'title': 'SONDA: notícias corporativas recentes',
        'source': 'SONDA',
        'url': 'https://www.sonda.com/pt/quem-somos/noticias',
        'reason': 'o material novo identificado é de workplace services; sem vínculo independente com mobilidade.',
    },
]

result = {
    'run_date': RUN_DATE,
    'window_start': WINDOW_START,
    'window_end': RUN_DATE,
    'scope': 'ABtec Mobilidade, associadas oficiais e agenda brasileira de tecnologia para mobilidade',
    'sources_checked': checked,
    'candidates_curated': curated,
    'discarded': discarded,
    'associate_check': {
        'associates_checked': ['Bus2', 'Cittati', 'Empresa 1', 'ONBOARD', 'Planeta Informática', 'Prodata Mobility Brasil', 'SONDA', 'Transdata'],
        'qualified_new_findings': ['ONBOARD — integração da bilhetagem digital ao Monitriip'],
        'note': 'Não foram localizados outros achados novos, abertos e diretamente aderentes às associadas na janela. CittaMobi não foi atribuído à Cittati por ausência de vínculo formal validado.',
    },
    'editorial_notes': [
        'O link arquivado é o artigo aberto do Diário do Transporte, validado por título, data, associada e assunto. A página institucional da ANTT foi consultada como confirmação do papel do Monitriip.',
        'O achado é assunto monitorado, não tendência validada: ainda não há recorrência, diversidade de casos ou evidência pública de adoção para qualificá-lo como tendência.',
        'Nenhuma página pública, índice ou edição semanal foi alterada.',
    ],
}

OUT.mkdir(exist_ok=True)
(OUT / f'incremental_radar_abtec_{RUN_DATE}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / f'achados_curados_radar_abtec_{RUN_DATE}.json').write_text(json.dumps(curated, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

with (OUT / f'incremental_radar_abtec_{RUN_DATE}.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['tipo', 'fonte', 'titulo', 'url', 'status'])
    writer.writeheader()
    for item in checked:
        writer.writerow({'tipo': 'fonte_verificada', 'fonte': item['source'], 'titulo': '', 'url': item['url'], 'status': item['result']})
    for item in curated:
        writer.writerow({'tipo': 'achado_curado', 'fonte': item['source'], 'titulo': item['title'], 'url': item['url'], 'status': item['maturity']})
    for item in discarded:
        writer.writerow({'tipo': 'descarte', 'fonte': item['source'], 'titulo': item['title'], 'url': item['url'], 'status': item['reason']})

with (OUT / f'achados_curados_radar_abtec_{RUN_DATE}.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'cluster', 'maturidade', 'titulo', 'fonte', 'data', 'url', 'associadas', 'status_link', 'citation'])
    writer.writeheader()
    for item in curated:
        writer.writerow({'id': item['id'], 'cluster': item['cluster'], 'maturidade': item['maturity'], 'titulo': item['title'], 'fonte': item['source'], 'data': item['published_date'], 'url': item['url'], 'associadas': '; '.join(item['associates']), 'status_link': item['link_status'], 'citation': item['citation']})

summary = '''# Radar ABtec Mobilidade — resumo diário

**Data de referência:** 23/10/2026  
**Janela incremental:** 22–23/10/2026  
**Status:** coleta interna concluída; nenhuma página pública foi alterada.[unverified]

## Fontes efetivamente verificadas
Foram verificadas **26 fontes diretas**: ABtec Mobilidade e as oito associadas; NTU, Semove Rio, ABRATI, FETPESP, ANTP e ANPTrilhos; Diário do Transporte, Technibus, Via Trolebus, Mobilize, Frota&Cia e Connected Smart Cities; BNDES, Ministério das Cidades, WRI Brasil e ITDP Brasil.[unverified] **25 estavam acessíveis**; Semove Rio retornou HTTP 403.[unverified]

## Achado novo curado

### Bilhetagem digital e dados regulatórios — assunto monitorado
A ONBOARD anunciou a integração de sua plataforma de bilhetagem digital ao Monitriip, sistema de monitoramento do transporte rodoviário interestadual e internacional de passageiros da ANTT.[1] O Monitriip é disciplinado por padrão de dados que inclui coleta, armazenamento, disponibilização e envio para acompanhamento da operação.[2] Para o Radar, o sinal conecta bilhetagem digital e dados operacionais à infraestrutura regulatória federal; a fonte pública ainda não especifica escopo contratual, cronograma, operadores atendidos ou indicadores de adoção.[1]

## Associadas ABtec
A ONBOARD foi a única associada com achado incremental aberto e diretamente aderente na janela.[1] Não foram localizados outros achados novos qualificados para Bus2, Cittati, Empresa 1, Planeta Informática, Prodata Mobility Brasil, SONDA ou Transdata.[unverified] CittaMobi segue sem atribuição à Cittati por ausência de vínculo formal validado.[unverified]

## Descartes relevantes
- Circuitos turísticos de ônibus elétricos, restrição pontual na Linha 11-Coral e renovação administrativa da Next Mobilidade: sem camada tecnológica, de dados ou de inovação setorial verificável.[unverified]
- Leitura de mercado da Mercedes-Benz e notícia corporativa da SONDA sobre workplace services: sem aderência direta ao recorte de mobilidade tecnológica.[unverified]
- Homônimos de SONDA e ONBOARD permanecem excluídos sem vínculo independente com mobilidade.[unverified]

## Cluster a acompanhar
1. **Bilhetagem digital e dados regulatórios:** confirmar operadores, cobertura, interoperabilidade, requisitos de transmissão de dados e resultados da integração ONBOARD–Monitriip antes de promover o assunto a tendência candidata.[1][2]
'''
(OUT / f'resumo_incremental_radar_abtec_{RUN_DATE}.md').write_text(summary, encoding='utf-8')
(OUT / f'resumo_curado_radar_abtec_{RUN_DATE}.md').write_text(summary, encoding='utf-8')

source_map = ROOT / 'fontes' / 'fontes_setoriais_validadas.csv'
rows = list(csv.DictReader(source_map.open(encoding='utf-8'), delimiter=';'))
for row in rows:
    row.pop(None, None)
status_by_name = {item['source']: item['result'].replace('acessível', 'acessível').replace('HTTP 403', 'bloqueio_403') for item in checked}
for row in rows:
    row['status_2026-10-23'] = status_by_name.get(row['nome'], 'não_verificado')
    row['observacao'] = f"{row['observacao']} | verificação direta em 23/10/2026: {row['status_2026-10-23']}"
fields = ['nome', 'classe', 'url_oficial', 'status_2026-10-22', 'status_2026-10-23', 'observacao']
with source_map.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields, delimiter=';')
    writer.writeheader()
    writer.writerows(rows)

print(json.dumps({'sources_checked': len(checked), 'accessible': sum(x['accessible'] for x in checked), 'curated': len(curated), 'discarded': len(discarded)}, ensure_ascii=False))
