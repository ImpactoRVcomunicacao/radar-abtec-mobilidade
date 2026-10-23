#!/usr/bin/env python3
"""Direct-source probe for the ABtec daily incremental scan (23 Oct 2026)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT = Path('/opt/data/abtec_mobilidade_inteligencia')
OUT = ROOT / 'buscas'
RUN_DATE = '2026-10-23'
SOURCES = [
    ('ABtec Mobilidade — releases', 'associacao', 'https://abtecbr.org/comunicacao/releases'),
    ('ABtec Mobilidade — notícias', 'associacao', 'https://abtecbr.org/comunicacao/noticias'),
    ('Bus2 — blog', 'associada', 'https://bus2.blog/'),
    ('Cittati — blog', 'associada', 'https://www.cittati.com.br/blog'),
    ('Empresa 1 — transporte', 'associada', 'https://www.empresa1.com.br/categoria/transporte/'),
    ('ONBOARD — publicações', 'associada', 'https://onboard.com.br/blog'),
    ('Planeta Informática — notícias', 'associada', 'https://www.planeta.inf.br/noticias/'),
    ('Prodata Mobility Brasil', 'associada', 'https://www.prodatamobility.com.br/'),
    ('SONDA — notícias', 'associada', 'https://www.sonda.com/pt/quem-somos/noticias'),
    ('Transdata', 'associada', 'https://www.itstransdata.com/'),
    ('NTU', 'entidade', 'https://www.ntu.org.br/'),
    ('Semove Rio', 'entidade', 'https://semove.org.br/'),
    ('ABRATI', 'entidade', 'https://www.abrati.org.br/'),
    ('FETPESP', 'entidade', 'https://fetpesp.org.br/'),
    ('ANTP', 'entidade', 'https://antp.org.br/'),
    ('ANPTrilhos', 'entidade', 'https://anptrilhos.org.br/'),
    ('Diário do Transporte', 'imprensa_setorial', 'https://diariodotransporte.com.br/'),
    ('Technibus', 'imprensa_setorial', 'https://technibus.com.br/'),
    ('Via Trolebus', 'imprensa_setorial', 'https://viatrolebus.com.br/'),
    ('Mobilize', 'imprensa_setorial', 'https://www.mobilize.org.br/'),
    ('Frota&Cia', 'imprensa_setorial', 'https://frotacia.com.br/'),
    ('Connected Smart Cities', 'setorial', 'https://plataformacsc.com.br/'),
    ('BNDES', 'institucional', 'https://www.bndes.gov.br/wps/portal/site/home'),
    ('Ministério das Cidades', 'institucional', 'https://www.gov.br/cidades/pt-br/assuntos/mobilidade-urbana'),
    ('WRI Brasil', 'institucional', 'https://www.wribrasil.org.br/'),
    ('ITDP Brasil', 'institucional', 'https://itdpbrasil.org/'),
]
KEYWORDS = re.compile(r'\b(mobilidade|transporte|ônibus|onibus|bilhet|pagamento|pix|emv|its|avl|operação|operacao|passageiro|dados|inteligência artificial|inteligencia artificial|smart cit|elétric|eletric|integração|integracao|telemetria|segurança|seguranca|metrô|metro|trilho)\b', re.I)
DATE_PATTERNS = ('2026/10/23', '23/10/2026', '2026-10-23', '23 de outubro de 2026')
USER_AGENT = 'Mozilla/5.0 (compatible; ImpactoRV-RadarABtec/1.0; +https://abtecbr.org/)'


def probe(name: str, kind: str, url: str) -> dict:
    item = {'source': name, 'class': kind, 'url': url}
    try:
        req = Request(url, headers={'User-Agent': USER_AGENT})
        with urlopen(req, timeout=25) as response:
            raw = response.read()
            final_url = response.geturl()
            status = response.status
        item.update({'status': status, 'final_url': final_url, 'accessible': 200 <= status < 400, 'bytes': len(raw)})
        text = raw.decode('utf-8', errors='replace')
        title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.I | re.S)
        title = re.sub(r'<[^>]+>', ' ', title_match.group(1)) if title_match else ''
        item['page_title'] = ' '.join(unescape(title).split())[:240]
        candidates = []
        seen = set()
        for match in re.finditer(r'<a\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*>(.*?)</a>', text, re.I | re.S):
            href_value, label_html = match.groups()
            label = ' '.join(unescape(re.sub(r'<[^>]+>', ' ', label_html)).split())
            href = urljoin(final_url, unescape(href_value))
            if not label or href in seen or not href.startswith(('http://', 'https://')):
                continue
            seen.add(href)
            start, end = max(0, match.start() - 450), min(len(text), match.end() + 450)
            context = ' '.join(unescape(re.sub(r'<[^>]+>', ' ', text[start:end])).split())
            haystack = f'{label} {context} {href}'
            if KEYWORDS.search(haystack) or any(p in haystack.lower() for p in DATE_PATTERNS):
                candidates.append({'title': label[:300], 'url': href, 'date_hint_today': any(p in haystack.lower() for p in DATE_PATTERNS), 'context': context[:600]})
        item['result'] = 'acessível'
        item['candidate_links'] = candidates[:60]
    except HTTPError as exc:
        item.update({'status': exc.code, 'accessible': False, 'result': f'HTTP {exc.code}'})
    except (URLError, TimeoutError, OSError) as exc:
        item.update({'status': None, 'accessible': False, 'result': f'{type(exc).__name__}: {exc}'})
    return item


def main() -> None:
    results = [probe(*source) for source in SOURCES]
    output = {
        'run_date': RUN_DATE,
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'sources_checked': results,
        'today_candidates': [
            {'source': x['source'], **candidate}
            for x in results for candidate in x.get('candidate_links', []) if candidate['date_hint_today']
        ],
    }
    OUT.mkdir(exist_ok=True)
    path = OUT / f'prova_fontes_radar_abtec_{RUN_DATE}.json'
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checked': len(results), 'accessible': sum(x['accessible'] for x in results), 'today_candidates': len(output['today_candidates']), 'path': str(path)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
