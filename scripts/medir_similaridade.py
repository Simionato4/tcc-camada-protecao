"""Quase-duplicatas na amostra de revisao do HackAPrompt (ADR-0017, quarta rodada).

LEITURA PURA: nao grava nada, nao imprime texto de ataque — so ordens e razoes.

A deduplicacao do universo elimina apenas textos identicos (ADR-0017, decisao original).
Variacoes minimas do mesmo ataque sobrevivem, e reduzem o numero de ataques distintos que
cada estrato da amostra realmente contem. Este script **descreve** isso; nao filtra nem
reclassifica nada.

Medida: `difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()` entre os textos de
dois casos do mesmo estrato, sobre o `user_input` do CSV de revisao com as quebras de
linha restauradas. LIMIAR e ponto de corte descritivo, nao parametro do experimento.

Uso:
    python scripts/medir_similaridade.py conjunto_teste/revisao/hackaprompt_revisao.csv
"""

from __future__ import annotations

import csv
import difflib
import itertools
import sys
from pathlib import Path

LIMIAR = 0.8


def ler(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo, delimiter=";"))
    for linha in linhas:
        linha["user_input"] = (
            linha["user_input"].replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
        )
    return linhas


def grupos(ordens: list[str], pares: list[tuple[str, str]]) -> list[list[str]]:
    """Componentes conexos: casos ligados por algum par acima do limiar."""
    pai = {o: o for o in ordens}

    def raiz(o: str) -> str:
        while pai[o] != o:
            pai[o] = pai[pai[o]]
            o = pai[o]
        return o

    for a, b in pares:
        pai[raiz(a)] = raiz(b)
    componentes: dict[str, list[str]] = {}
    for o in ordens:
        componentes.setdefault(raiz(o), []).append(o)
    return sorted(componentes.values(), key=lambda g: int(g[0]))


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    linhas = ler(Path(sys.argv[1]))
    classe = lambda l: (l.get("classe_final") or l["classe_automatica"]).strip()
    estratos: dict[str, list[dict]] = {}
    for linha in linhas:
        estratos.setdefault(classe(linha), []).append(linha)

    print(f"casos: {len(linhas)}; limiar descritivo: {LIMIAR}")
    for nome in sorted(estratos):
        casos = sorted(estratos[nome], key=lambda l: int(l["ordem"]))
        pares = []
        for a, b in itertools.combinations(casos, 2):
            razao = difflib.SequenceMatcher(
                None, a["user_input"], b["user_input"], autojunk=False
            ).ratio()
            if razao >= LIMIAR:
                pares.append((a["ordem"], b["ordem"], razao))
        g = grupos([c["ordem"] for c in casos], [(a, b) for a, b, _ in pares])
        print()
        print(f"{nome}: {len(casos)} casos, {len(g)} grupos distintos")
        for a, b, razao in pares:
            print(f"  {a:>2} ~ {b:>2}  {razao:.3f}")
        for grupo in g:
            if len(grupo) > 1:
                print(f"  grupo: {', '.join(grupo)}")
    print()
    print("Nenhum arquivo gravado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
