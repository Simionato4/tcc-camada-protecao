"""Sanidade do Presidio em portugues (RQ-11, ADR-0022).

Envia ao Presidio analyzer adaptado os textos do CONJUNTO DE DESENVOLVIMENTO e resume
o que ele detecta. Prova que a condicao C aceita language="pt" e funciona sobre texto
em portugues antes do congelamento. Nao e a medicao do experimento: nada aqui e usado
para ajustar o Presidio, cuja configuracao foi fixada antes (presidio-analyzer/conf/).

Recusa qualquer arquivo de conjunto_teste/: o conjunto de teste nunca e submetido
antes da execucao.

Uso:  python scripts/sanidade_presidio_pt.py [--limite N]
      --limite N: so os N primeiros textos (para uma conferencia rapida)
Saida: resumo no terminal e registro bruto em resultados/sanidade_presidio_pt_<data>.json
So biblioteca padrao.
"""

from __future__ import annotations

import collections
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CORPUS = RAIZ / "conjunto_desenvolvimento" / "pii" / "corpus.jsonl"
URL = "http://localhost:5002/analyze"
# Parametros enviados: so texto e idioma. Entidades e limiar ficam no padrao (ADR-0022).
IDIOMA = "pt"
# Entidades do Presidio que correspondem aos 7 tipos avaliados (protocolo 8.4, FP (ii)).
CORRESPONDENTES = {"EMAIL_ADDRESS", "PHONE_NUMBER"}


def analisar(texto: str) -> list[dict]:
    corpo = json.dumps({"text": texto, "language": IDIOMA}).encode("utf-8")
    req = urllib.request.Request(URL, data=corpo, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def coberto(inicio: int, fim: int, trechos: list[tuple[int, int]]) -> bool:
    """Toda posicao de [inicio, fim) esta em algum trecho detectado."""
    return all(any(a <= p < b for a, b in trechos) for p in range(inicio, fim))


def sobrepoe(inicio: int, fim: int, a: int, b: int) -> bool:
    return inicio < b and a < fim


def main() -> int:
    if "conjunto_teste" in CORPUS.parts:
        print("recusado: o conjunto de teste nao e submetido antes da execucao")
        return 2
    registros = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines() if l.strip()]
    if "--limite" in sys.argv:
        registros = registros[: int(sys.argv[sys.argv.index("--limite") + 1])]
    inicio_total = time.perf_counter()

    pos = collections.Counter()
    pos_cob = collections.Counter()
    pos_parcial = collections.Counter()
    neg = collections.Counter()
    neg_tocado = collections.Counter()
    extras = collections.Counter()
    bruto = []

    for i, r in enumerate(registros, 1):
        t0 = time.perf_counter()
        deteccoes = analisar(r["texto"])
        if i == 1 or i % 25 == 0 or i == len(registros):
            print(f"  {i}/{len(registros)} textos  ultimo: {(time.perf_counter() - t0) * 1000:.0f} ms"
                  f"  total: {time.perf_counter() - inicio_total:.0f} s", flush=True)
        trechos = [(d["start"], d["end"]) for d in deteccoes]
        bruto.append({"id": r["id"], "deteccoes": deteccoes})
        for o in r["ocorrencias"]:
            t = o["tipo"]
            if o["polaridade"] == "positivo":
                pos[t] += 1
                if coberto(o["inicio"], o["fim"], trechos):
                    pos_cob[t] += 1
                elif any(sobrepoe(o["inicio"], o["fim"], a, b) for a, b in trechos):
                    pos_parcial[t] += 1
            else:
                neg[t] += 1
                if any(sobrepoe(o["inicio"], o["fim"], a, b) for a, b in trechos):
                    neg_tocado[t] += 1
        for d in deteccoes:
            if not any(sobrepoe(o["inicio"], o["fim"], d["start"], d["end"]) for o in r["ocorrencias"]):
                extras[d["entity_type"]] += 1

    print(f"Presidio {URL}  language={IDIOMA}  textos={len(registros)}  fonte={CORPUS.relative_to(RAIZ)}")
    print()
    print(f"{'tipo':<10}{'positivos cobertos':>20}{'cobertura parcial':>19}{'negativos tocados':>19}")
    for t in sorted(set(pos) | set(neg)):
        print(f"{t:<10}{pos_cob[t]:>14} / {pos[t]:<3}{pos_parcial[t]:>19}{neg_tocado[t]:>13} / {neg[t]:<3}")
    print()
    print("Trechos fora do gabarito, por entidade do Presidio:")
    for ent, n in extras.most_common():
        marca = "conta como FP (ii)" if ent in CORRESPONDENTES else "fora dos 7 tipos: tabela a parte"
        print(f"  {ent:<16}{n:>5}   {marca}")
    if not extras:
        print("  nenhum")

    saida = RAIZ / "resultados" / f"sanidade_presidio_pt_{dt.date.today().isoformat()}.json"
    saida.write_text(
        json.dumps({"url": URL, "idioma": IDIOMA, "fonte": str(CORPUS.relative_to(RAIZ)),
                    "registros": bruto}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\nregistro bruto: {saida.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
