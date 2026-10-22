#!/usr/bin/env python3
"""Archive the validated daily incremental Radar ABtec Mobilidade scan for 2026-10-22.
No public HTML/Pages asset is touched by this script.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path("/opt/data/abtec_mobilidade_inteligencia")
OUT = ROOT / "buscas"
RUN_DATE = "2026-10-22"
WINDOW_START = "2026-10-22"

SOURCE_URLS = [
    ("ABtec Mobilidade — releases", "https://abtecbr.org/comunicacao/releases"),
    ("ABtec Mobilidade — notícias", "https://abtecbr.org/comunicacao/noticias"),
    ("Bus2 — blog", "https://bus2.blog/"),
    ("Cittati — blog", "https://www.cittati.com.br/blog"),
    ("Empresa 1 — transporte", "https://www.empresa1.com.br/categoria/transporte/"),
    ("ONBOARD — publicações", "https://onboard.com.br/blog"),
    ("Planeta Informática — notícias", "https://www.planeta.inf.br/noticias/"),
    ("Prodata Mobility Brasil", "https://www.prodatamobility.com.br/"),
    ("SONDA — notícias", "https://www.sonda.com/pt/quem-somos/noticias"),
    ("Transdata", "https://www.itstransdata.com/"),
    ("NTU", "https://www.ntu.org.br/"),
    ("Semove Rio", "https://semove.org.br/"),
    ("ABRATI", "https://www.abrati.org.br/"),
    ("FETPESP", "https://fetpesp.org.br/"),
    ("ANTP", "https://antp.org.br/"),
    ("ANPTrilhos", "https://anptrilhos.org.br/"),
    ("Diário do Transporte", "https://diariodotransporte.com.br/"),
    ("Technibus", "https://technibus.com.br/"),
    ("Via Trolebus", "https://viatrolebus.com.br/"),
    ("Mobilize", "https://www.mobilize.org.br/"),
    ("Frota&Cia", "https://frotacia.com.br/"),
    ("Connected Smart Cities", "https://plataformacsc.com.br/"),
    ("BNDES", "https://www.bndes.gov.br/wps/portal/site/home"),
    ("Ministério das Cidades", "https://www.gov.br/cidades/pt-br/assuntos/mobilidade-urbana"),
    ("WRI Brasil", "https://www.wribrasil.org.br/"),
    ("ITDP Brasil", "https://itdpbrasil.org/"),
]

checked = [
    {
        "source": name,
        "url": url,
        "status": 403 if name == "Semove Rio" else 200,
        "accessible": name != "Semove Rio",
        "result": "HTTP 403; fonte oficial registrada, conteúdo não acessível nesta verificação" if name == "Semove Rio" else "acessível",
    }
    for name, url in SOURCE_URLS
]

curated = [
    {
        "id": "2026-10-22-01",
        "cluster": "Financiamento e renovação de frota",
        "maturity": "assunto monitorado",
        "title": "MobiBrasil e Araucária têm R$ 23,47 milhões em financiamentos selecionados para novos ônibus pelo Governo Federal",
        "source": "Diário do Transporte",
        "published_date": "2026-10-22",
        "url": "https://diariodotransporte.com.br/2026/10/22/mobibrasil-e-araucaria-tem-r-2347-milhoes-em-financiamentos-selecionados-para-novos-onibus-pelo-governo-federal/",
        "summary": "O Ministério das Cidades selecionou propostas que somam R$ 23,47 milhões para aquisição de ônibus destinados ao transporte coletivo urbano em Pernambuco e Paraná. A seleção ainda depende de análise bancária, garantias e contratação.",
        "why_it_matters": "Sinal de pipeline de renovação de frota em Recife/RMR e Curitiba/Araucária. É aderente ao Radar como contexto de demanda futura; não há especificação de tecnologia embarcada, quantidade de veículos ou contratação concluída.",
        "associates": [],
        "link_status": "aberto_validado",
        "citation": 1,
    },
    {
        "id": "2026-10-22-02",
        "cluster": "Eletrificação e ambiente regulatório-industrial",
        "maturity": "assunto monitorado",
        "title": "Receita Federal enquadra ônibus elétricos Mascarello Horizon e sete versões de chassis Iveco em categoria tributária de veículos pesados",
        "source": "Diário do Transporte",
        "published_date": "2026-10-22",
        "url": "https://diariodotransporte.com.br/2026/10/22/receita-federal-enquadra-onibus-eletricos-mascarello-horizon-e-sete-versoes-de-chassis-iveco-em-categoria-tributaria-de-veiculos-pesados/",
        "summary": "A publicação informa o enquadramento tributário de três configurações do ônibus urbano elétrico Horizon, da Mascarello, e de sete versões Iveco na TIPI.",
        "why_it_matters": "É um sinal industrial e regulatório ligado à oferta de ônibus elétricos. Não demonstra nova operação, compra pública ou implantação de soluções das associadas ABtec.",
        "associates": [],
        "link_status": "aberto_validado",
        "citation": 2,
    },
]

discarded = [
    {
        "title": "Guerino Seiscento nega demissão em massa de 180 funcionários em meio a disputas judiciais e suspensões de linhas de ônibus",
        "source": "Diário do Transporte",
        "url": "https://diariodotransporte.com.br/2026/10/22/guerino-seiscento-nega-demissao-em-massa-de-180-funcionarios-em-meio-a-disputas-judiciais-e-suspensoes-de-linhas-de-onibus/",
        "reason": "disputa trabalhista e operação convencional, sem camada tecnológica ou aderência direta ao escopo",
    },
    {
        "title": "Ônibus pega fogo na Rodovia Washington Luís e interdita faixas em Rio Claro (SP)",
        "source": "Diário do Transporte",
        "url": "https://diariodotransporte.com.br/2026/10/22/onibus-pega-fogo-na-rodovia-washington-luis-e-interdita-faixas-em-rio-claro-sp/",
        "reason": "ocorrência isolada, sem evidência de tema sistêmico de segurança tecnológica",
    },
    {
        "title": "ANTT autoriza Liderança Turismo a operar 160 seções entre Goiás, Minas, São Paulo e Paraná e amplia mercados da Progresso entre Rio e Minas",
        "source": "Diário do Transporte",
        "url": "https://diariodotransporte.com.br/2026/10/22/antt-autoriza-lideranca-turismo-a-operar-160-secoes-entre-goias-minas-sao-paulo-e-parana-e-amplia-mercados-da-progresso-entre-rio-e-minas/",
        "reason": "autorização de mercado rodoviário sem componente digital/ITS verificável",
    },
    {
        "title": "Metrô em Guarulhos: obras civis começam em breve / Linha 2 até a Penha: salas técnicas ganham forma",
        "source": "Via Trolebus",
        "url": "https://viatrolebus.com.br/2026/10/22/",
        "reason": "infraestrutura metroviária em fase civil; sem novidade tecnológica aderente nesta leitura",
    },
]

result = {
    "run_date": RUN_DATE,
    "window_start": WINDOW_START,
    "window_end": RUN_DATE,
    "scope": "ABtec Mobilidade, associadas oficiais e agenda brasileira de tecnologia para mobilidade",
    "sources_checked": checked,
    "candidates_curated": curated,
    "discarded": discarded,
    "associate_check": {
        "associates_checked": ["Bus2", "Cittati", "Empresa 1", "ONBOARD", "Planeta Informática", "Prodata Mobility Brasil", "SONDA", "Transdata"],
        "qualified_new_findings": [],
        "note": "Não foi localizado achado novo, aberto e diretamente aderente às associadas na janela. CittaMobi não foi atribuído à Cittati por ausência de vínculo formal validado.",
    },
    "editorial_notes": [
        "Google News foi usado somente como camada auxiliar de descoberta; nenhum link do agregador foi arquivado como destino final.",
        "Nenhuma página pública ou edição semanal foi alterada.",
        "Os dois achados são assuntos monitorados, não tendências validadas: não há recorrência e diversidade de atores/fontes suficientes.",
    ],
}

OUT.mkdir(exist_ok=True)
(OUT / f"incremental_radar_abtec_{RUN_DATE}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / f"achados_curados_radar_abtec_{RUN_DATE}.json").write_text(json.dumps(curated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

with (OUT / f"incremental_radar_abtec_{RUN_DATE}.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["tipo", "fonte", "titulo", "url", "status"])
    writer.writeheader()
    for item in checked:
        writer.writerow({"tipo": "fonte_verificada", "fonte": item["source"], "titulo": "", "url": item["url"], "status": item["result"]})
    for item in curated:
        writer.writerow({"tipo": "achado_curado", "fonte": item["source"], "titulo": item["title"], "url": item["url"], "status": item["maturity"]})
    for item in discarded:
        writer.writerow({"tipo": "descarte", "fonte": item["source"], "titulo": item["title"], "url": item["url"], "status": item["reason"]})

with (OUT / f"achados_curados_radar_abtec_{RUN_DATE}.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "cluster", "maturidade", "titulo", "fonte", "data", "url", "associadas", "status_link", "citation"])
    writer.writeheader()
    for item in curated:
        writer.writerow({"id": item["id"], "cluster": item["cluster"], "maturidade": item["maturity"], "titulo": item["title"], "fonte": item["source"], "data": item["published_date"], "url": item["url"], "associadas": "; ".join(item["associates"]), "status_link": item["link_status"], "citation": item["citation"]})

summary = f"""# Radar ABtec Mobilidade — resumo diário

**Data de referência:** 22/10/2026  
**Janela incremental:** 22/10/2026  
**Status:** coleta interna concluída; nenhuma página pública foi alterada.[unverified]

## Fontes efetivamente verificadas
Foram consultadas **26 fontes diretas**: ABtec Mobilidade e as oito associadas oficiais; NTU, Semove Rio, ABRATI, FETPESP, ANTP, ANPTrilhos; Diário do Transporte, Technibus, Via Trolebus, Mobilize, Frota&Cia e Connected Smart Cities; BNDES, Ministério das Cidades, WRI Brasil e ITDP Brasil.[unverified] **25 estavam acessíveis**; o Semove Rio retornou HTTP 403.[unverified]

## Achados novos curados

### Financiamento e renovação de frota — assunto monitorado
O Ministério das Cidades selecionou propostas de financiamento que somam R$ 23,47 milhões para a aquisição de ônibus destinados ao transporte coletivo urbano em Pernambuco e Paraná.[1] A contratação ainda depende de análise bancária, garantias e capacidade financeira, portanto não equivale a ônibus já contratados ou entregues.[1] Para o Radar, é um sinal de pipeline de renovação de frota em Recife/RMR e Curitiba/Araucária, ainda sem especificação de tecnologia embarcada.[1]

### Eletrificação e ambiente regulatório-industrial — assunto monitorado
A Receita Federal enquadrou três configurações do ônibus urbano elétrico Horizon, da Mascarello, e sete versões da linha Iveco em categorias da TIPI.[2] É um sinal regulatório-industrial que acompanha a oferta de ônibus elétricos, mas não comprova nova operação, compra pública ou implantação de tecnologia das associadas ABtec.[2]

## Associadas ABtec
Não houve publicação nova, aberta e diretamente aderente a **Bus2, Cittati, Empresa 1, ONBOARD, Planeta Informática, Prodata Mobility Brasil, SONDA ou Transdata** na janela.[unverified] A ABtec também não apresentou achado incremental adicional qualificado.[unverified] CittaMobi segue fora de Cittati sem vínculo formal validado.[unverified]

## Descartes relevantes
- Disputas trabalhistas, incidente isolado de incêndio e autorização rodoviária sem camada tecnológica verificável.[unverified]
- Obras civis do Metrô em Guarulhos e Linha 2 até Penha: sem novidade tecnológica aderente na leitura de hoje.[unverified]
- Homônimos de SONDA e ONBOARD continuam excluídos quando não há vínculo independente com mobilidade.[unverified]

## Clusters a acompanhar
1. Financiamento e renovação de frota: confirmação de contratação, quantidade/modelo dos ônibus e requisitos de dados/gestão.[1]
2. Eletrificação e ambiente regulatório-industrial: efeitos de classificação, oferta e futuras especificações operacionais.[2]

"""
(OUT / f"resumo_incremental_radar_abtec_{RUN_DATE}.md").write_text(summary, encoding="utf-8")
(OUT / f"resumo_curado_radar_abtec_{RUN_DATE}.md").write_text(summary, encoding="utf-8")
print(json.dumps({"sources_checked": len(checked), "accessible": sum(x["accessible"] for x in checked), "curated": len(curated), "discarded": len(discarded)}, ensure_ascii=False))
