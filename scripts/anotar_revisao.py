"""Anota `classe_revisada` no CSV de revisao, sem passar pelo Excel.

Por que existe. O Excel ja causou tres incidentes neste projeto: trava exclusiva que
derrubou uma execucao no meio, revisao sobrescrita, e uma edicao que nao persistiu e
produziu um registro afirmando reversao que nao ocorreu. Para corrigir poucos rotulos, o
Excel e um passo manual de risco desnecessario.

Este script nao substitui a revisao manual: ele registra uma decisao **que o autor ja
tomou**, lendo o caso no CSV. O julgamento continua humano; o que sai do caminho e a
planilha.

Escrita atomica, com validacao da classe contra `classificar_codificacao.CLASSES`. Nao
imprime texto de ataque.

Uso:
    python scripts/anotar_revisao.py 22=texto_simples 28=texto_simples 30=texto_simples
    python scripts/anotar_revisao.py --listar
    python scripts/anotar_revisao.py 14=                 # limpa a anotacao da ordem 14
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REVISAO = RAIZ / "conjunto_teste" / "revisao" / "hackaprompt_revisao.csv"
DELIMITADOR = ";"
CODIFICACAO = "utf-8-sig"

_spec = importlib.util.spec_from_file_location(
    "classificar_codificacao", RAIZ / "scripts" / "classificar_codificacao.py"
)
clf = importlib.util.module_from_spec(_spec)
sys.modules["classificar_codificacao"] = clf
_spec.loader.exec_module(clf)


def ler() -> tuple[list[str], list[dict[str, str]]]:
    with REVISAO.open(encoding=CODIFICACAO, newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=DELIMITADOR)
        return list(leitor.fieldnames or []), list(leitor)


def gravar(cabecalho: list[str], linhas: list[dict[str, str]]) -> None:
    """Grava em arquivo temporario e substitui: ou troca inteiro, ou nao troca."""
    buffer = io.StringIO(newline="")
    escritor = csv.DictWriter(
        buffer, fieldnames=cabecalho, delimiter=DELIMITADOR, lineterminator="\r\n"
    )
    escritor.writeheader()
    escritor.writerows(linhas)
    temporario = REVISAO.with_suffix(REVISAO.suffix + ".tmp")
    with temporario.open("w", encoding=CODIFICACAO, newline="") as arquivo:
        arquivo.write(buffer.getvalue())
    os.replace(temporario, REVISAO)


def listar(linhas: list[dict[str, str]]) -> None:
    print(f"{'ordem':>6} | {'automatica':28} | {'herdada':28} | revisada")
    for linha in linhas:
        print(
            f"{linha['ordem']:>6} | {linha.get('classe_automatica', ''):28} "
            f"| {linha.get('classe_herdada', ''):28} | {linha.get('classe_revisada', '')}"
        )


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument(
        "anotacoes",
        nargs="*",
        help="pares ordem=classe; classe vazia limpa a anotacao",
    )
    analisador.add_argument("--listar", action="store_true")
    argumentos = analisador.parse_args()

    if not REVISAO.exists():
        print(f"arquivo nao encontrado: {REVISAO}", file=sys.stderr)
        return 2

    cabecalho, linhas = ler()
    if "classe_revisada" not in cabecalho:
        print("o CSV nao tem coluna `classe_revisada`", file=sys.stderr)
        return 2

    if argumentos.listar or not argumentos.anotacoes:
        listar(linhas)
        return 0

    por_ordem = {linha["ordem"]: linha for linha in linhas}
    pedidos: list[tuple[str, str]] = []
    for item in argumentos.anotacoes:
        if "=" not in item:
            print(f"formato invalido: {item!r} (use ordem=classe)", file=sys.stderr)
            return 2
        ordem, classe = item.split("=", 1)
        ordem, classe = ordem.strip(), classe.strip()
        if ordem not in por_ordem:
            print(f"ordem inexistente no CSV: {ordem}", file=sys.stderr)
            return 2
        if classe and classe not in clf.CLASSES:
            print(f"classe invalida: {classe!r}", file=sys.stderr)
            print(f"validas: {', '.join(clf.CLASSES)}", file=sys.stderr)
            return 2
        pedidos.append((ordem, classe))

    print("alteracoes a gravar:")
    for ordem, classe in pedidos:
        linha = por_ordem[ordem]
        antes = linha.get("classe_revisada", "") or "(vazio)"
        depois = classe or "(vazio)"
        print(f"  ordem {ordem:>3}: {antes}  ->  {depois}")
        linha["classe_revisada"] = classe

    gravar(cabecalho, linhas)
    preenchidas = sum(1 for l in linhas if (l.get("classe_revisada") or "").strip())
    print(f"\ngravado. linhas com `classe_revisada` preenchida: {preenchidas}/{len(linhas)}")
    print("Agora rode: python scripts/amostrar_hackaprompt.py --aplicar-revisao")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
