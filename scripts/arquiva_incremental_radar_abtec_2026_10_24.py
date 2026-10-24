#!/usr/bin/env python3
"""Archive the validated daily incremental ABtec Radar scan for 2026-10-24.
No public page or weekly edition is modified.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path('/opt/data/abtec_mobilidade_inteligencia')
OUT = ROOT / 'buscas'
RUN_DATE = '2026-10-24'
WINDOW_START = '2026-10-23'

probe = json.loads((OUT / f'prova_fontes_radar_abtec_{RUN_DATE}.json').read_text(encoding='utf-8'))
checked = probe['sources_checked']

curated = [{
    'id': '2026-10-24-01',
    'cluster': 'Prioridade operacional e ITS urbano',
    'maturity': 'assunto monitorado',
    'title': 'Goiânia lança BRS com nove ônibus piso baixo e prioridade por fiscalização eletrônica e semáforos em tempo real',
    'source': 'Technibus',
    'published_date': '2026-10-23',
    'url': 'https://technibus.com.br/2026/10/23/goiania-recebe-9-onibus-piso-baixo-para-a-operacao-do-primeiro-bus-rapid-service-brs',
    'summary': 'Goiânia lançou o primeiro Bus Rapid Service (BRS) e entregou nove ônibus piso baixo para a operação. A proposta articula faixa preferencial, sinalização específica, fiscalização eletrônica e semáforos sincronizados e controlados em tempo real.',
    'why_it_matters': 'É um sinal aderente ao Radar por combinar prioridade operacional, fiscalização e controle semafórico em um arranjo de ITS urbano. A fonte aponta estimativa de ganho de velocidade de cerca de 30%, ainda sem dados públicos de desempenho em operação, arquitetura tecnológica, integração de dados ou fornecedores.',
    'associates': [],
    'link_status': 'aberto_validado',
    'citation': 1,
}]

discarded = [
    {
        'title': 'Primeiro ônibus elétrico BYD/Caio “micrão” piso baixo no padrão SPTrans',
        'source': 'Diário do Transporte',
        'url': 'https://diariodotransporte.com.br/2026/10/23/primeiro-onibus-eletrico-byd-caio-micrao-piso-baixo-fica-pronto-no-padrao-sptrans-e-passara-por-demonstracao-junto-a-operadores-e-a-prefeitura/',
        'reason': 'lançamento de produto de eletromobilidade sem vínculo novo com associadas ABtec, ITS, pagamentos ou dados operacionais no material consultado.',
    },
    {
        'title': 'ANTT prorroga lances da Janela Extraordinária de mercados interestaduais',
        'source': 'Diário do Transporte',
        'url': 'https://diariodotransporte.com.br/2026/10/24/em-primeira-mao-antt-prorroga-lances-da-janela-extraordinaria-ate-13-de-novembro-apos-decisoes-judiciais-envolvendo-catedral-progresso-e-amarelinho-veja-o-historico/',
        'reason': 'movimento regulatório e judicial relevante ao rodoviário, mas sem componente tecnológico aderente ao recorte nesta leitura.',
    },
    {
        'title': 'Gontijo recebe autorização prévia para linha Belo Horizonte–Unaí',
        'source': 'Diário do Transporte',
        'url': 'https://diariodotransporte.com.br/2026/10/24/em-primeira-mao-gontijo-recebe-autorizacao-previa-para-assumir-linha-de-onibus-belo-horizonte-unai-da-sertaneja-em-minas-gerais-pela-seinfra/',
        'reason': 'ato de autorização de linha sem inovação tecnológica, dados ou solução operacional nova verificável.',
    },
    {
        'title': 'Notícias corporativas recentes da SONDA',
        'source': 'SONDA',
        'url': 'https://www.sonda.com/pt/quem-somos/noticias',
        'reason': 'não foi identificado conteúdo novo com vínculo independente a mobilidade; homônimos e comunicação de workplace services seguem excluídos.',
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
        'qualified_new_findings': [],
        'note': 'Não foram localizados achados incrementais abertos e diretamente aderentes às associadas na janela. CittaMobi não foi atribuído à Cittati por ausência de vínculo formal validado.',
    },
    'editorial_notes': [
        'O link curado foi aberto e validado por título, data, tema e fonte original.',
        'O BRS de Goiânia é assunto monitorado, não tendência candidata: há uma única implementação noticiada e ainda faltam resultados de operação e diversidade de casos.',
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

**Data de referência:** 24/10/2026  
**Janela incremental:** 23–24/10/2026  
**Status:** coleta interna concluída; nenhuma página pública foi alterada.[unverified]

## Fontes efetivamente verificadas
Foram verificadas **26 fontes diretas**: ABtec Mobilidade e as oito associadas; NTU, Semove Rio, ABRATI, FETPESP, ANTP e ANPTrilhos; Diário do Transporte, Technibus, Via Trolebus, Mobilize, Frota&Cia e Connected Smart Cities; BNDES, Ministério das Cidades, WRI Brasil e ITDP Brasil.[unverified] **25 estavam acessíveis**; Semove Rio retornou HTTP 403.[unverified]

## Achado novo curado
### Prioridade operacional e ITS urbano — assunto monitorado
Goiânia lançou o primeiro Bus Rapid Service (BRS) e entregou nove ônibus piso baixo. A proposta combina faixa preferencial, sinalização específica, fiscalização eletrônica e semáforos sincronizados e controlados em tempo real.[1] Para o Radar, é um sinal de ITS urbano aplicado à prioridade operacional; a fonte ainda não traz resultados em operação, arquitetura tecnológica, integração de dados ou fornecedores.[1]

## Associadas ABtec
Não foram localizados achados incrementais abertos e diretamente aderentes para Bus2, Cittati, Empresa 1, ONBOARD, Planeta Informática, Prodata Mobility Brasil, SONDA ou Transdata na janela.[unverified] CittaMobi permanece sem atribuição à Cittati por ausência de vínculo formal validado.[unverified]

## Descartes relevantes
- Ônibus elétrico BYD/Caio para padrão SPTrans: lançamento de produto sem vínculo novo com associadas ABtec, ITS, pagamentos ou dados operacionais no material consultado.[unverified]
- Prorrogação da Janela Extraordinária da ANTT e autorização de linha em Minas Gerais: movimentos regulatórios sem componente tecnológico aderente nesta leitura.[unverified]
- Comunicação recente da SONDA: conteúdo corporativo sem vínculo independente com mobilidade; homônimos continuam excluídos.[unverified]

## Cluster a acompanhar
1. **Prioridade operacional e ITS urbano:** acompanhar a implantação do BRS de Goiânia e buscar dados de velocidade, regularidade, fiscalização, controle semafórico, integração de dados e replicabilidade antes de promovê-lo a tendência candidata.[1]

## Sources
'''
(OUT / f'resumo_incremental_radar_abtec_{RUN_DATE}.md').write_text(summary, encoding='utf-8')
(OUT / f'resumo_curado_radar_abtec_{RUN_DATE}.md').write_text(summary, encoding='utf-8')

source_map = ROOT / 'fontes' / 'fontes_setoriais_validadas.csv'
rows = list(csv.DictReader(source_map.open(encoding='utf-8'), delimiter=';'))
for row in rows:
    row.pop(None, None)
status_by_name = {item['source']: item['result'].replace('HTTP 403', 'bloqueio_403') for item in checked}
for row in rows:
    row['status_2026-10-24'] = status_by_name.get(row['nome'], 'não_verificado')
    row['observacao'] = f"{row['observacao']} | verificação direta em 24/10/2026: {row['status_2026-10-24']}"
fields = ['nome', 'classe', 'url_oficial', 'status_2026-10-22', 'status_2026-10-23', 'status_2026-10-24', 'observacao']
with source_map.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields, delimiter=';')
    writer.writeheader()
    writer.writerows(rows)

print(json.dumps({'sources_checked': len(checked), 'accessible': sum(x['accessible'] for x in checked), 'curated': len(curated), 'discarded': len(discarded)}, ensure_ascii=False))
