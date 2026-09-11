"""Tarefa 3.2 — inspeciona os conjuntos obtidos e confere contra a proposta.

A proposta aprovada declara numeros que precisam ser confirmados **antes** do
congelamento: 939 solicitacoes do Do-Not-Answer, 248 na area de vazamento de
informacao (136 de organizacao ou governo, 112 de privacidade individual), e 75
cargas do BIPIA em 15 categorias.

Se algum nao bater, a proposta precisa de nota corrigindo o numero — e isso so tem
conserto antes do congelamento.

Este script **apenas le e conta**. Nao seleciona, nao amostra e nao escreve nada no
conjunto de teste.

Uso:
    python scripts/conferir_conjuntos.py
    python scripts/conferir_conjuntos.py --arvore   # so lista os arquivos
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "conjunto_teste" / "origem"

ESPERADO = {
    "do_not_answer_total": 939,
    "vazamento_total": 248,
    "vazamento_organizacao": 136,
    "vazamento_individual": 112,
    "bipia_cargas": 75,
    "bipia_categorias": 15,
}

EXTENSOES_DADOS = {".csv", ".json", ".jsonl", ".parquet", ".tsv"}


def arvore(pasta: Path, limite: int = 40) -> None:
    arquivos = sorted(
        (p for p in pasta.rglob("*") if p.is_file() and ".git" not in p.parts),
        key=lambda p: -p.stat().st_size,
    )
    for p in arquivos[:limite]:
        print(f"  {p.stat().st_size:>12,}  {p.relative_to(pasta)}")
    if len(arquivos) > limite:
        print(f"  ... e mais {len(arquivos) - limite} arquivos")


def carregar(caminho: Path):
    import pandas as pd

    sufixo = caminho.suffix.lower()
    if sufixo == ".csv":
        return pd.read_csv(caminho)
    if sufixo == ".tsv":
        return pd.read_csv(caminho, sep="\t")
    if sufixo == ".parquet":
        return pd.read_parquet(caminho)
    if sufixo == ".jsonl":
        return pd.read_json(caminho, lines=True)
    if sufixo == ".json":
        return pd.read_json(caminho)
    raise ValueError(sufixo)


def conferir(rotulo: str, obtido: int) -> str:
    esperado = ESPERADO.get(rotulo)
    if esperado is None:
        return ""
    return "  CONFERE" if obtido == esperado else f"  DIVERGE (proposta: {esperado})"


def do_not_answer() -> None:
    pasta = ORIGEM / "do-not-answer"
    print("=" * 78)
    print("DO-NOT-ANSWER")
    print("=" * 78)
    if not pasta.exists():
        print("  nao obtido")
        return

    candidatos = [
        p for p in pasta.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSOES_DADOS and ".git" not in p.parts
    ]
    for caminho in sorted(candidatos, key=lambda p: -p.stat().st_size):
        try:
            quadro = carregar(caminho)
        except Exception as erro:  # noqa: BLE001
            print(f"\n  [{caminho.relative_to(pasta)}] nao lido: {type(erro).__name__}")
            continue
        print(f"\n  Arquivo: {caminho.relative_to(pasta)}")
        print(f"  Linhas: {len(quadro)}{conferir('do_not_answer_total', len(quadro))}")
        print(f"  Colunas: {list(quadro.columns)[:14]}")

        for coluna in ("risk_area", "types_of_harm"):
            if coluna in quadro.columns:
                print(f"\n  Distribuicao de `{coluna}`:")
                for valor, contagem in quadro[coluna].value_counts().items():
                    print(f"    {contagem:>5}  {valor}")

        # A area de vazamento sustenta a Taxa de Compensacao e o recorte de 248.
        # Correspondencia EXATA: procurar por "information" pegaria tambem
        # `Misinformation Harms`, que e outra area de risco e nao entra no recorte.
        if "risk_area" in quadro.columns:
            alvo = quadro[quadro["risk_area"].astype(str).str.strip() == "Information Hazards"]
            if len(alvo):
                print(f"\n  Area com 'information' no nome: {len(alvo)} linhas"
                      f"{conferir('vazamento_total', len(alvo))}")
                if "types_of_harm" in alvo.columns:
                    for valor, contagem in alvo["types_of_harm"].value_counts().items():
                        rotulo = ""
                        if contagem == ESPERADO["vazamento_organizacao"]:
                            rotulo = "  <- 136 da proposta"
                        elif contagem == ESPERADO["vazamento_individual"]:
                            rotulo = "  <- 112 da proposta"
                        print(f"    {contagem:>5}  {valor}{rotulo}")
        break


def hackaprompt() -> None:
    pasta = ORIGEM / "hackaprompt"
    print()
    print("=" * 78)
    print("HACKAPROMPT")
    print("=" * 78)
    if not pasta.exists():
        print("  nao obtido")
        return
    for caminho in sorted(pasta.rglob("*.parquet"), key=lambda p: -p.stat().st_size):
        try:
            quadro = carregar(caminho)
        except Exception as erro:  # noqa: BLE001
            print(f"  [{caminho.name}] nao lido: {type(erro).__name__}: {erro}")
            continue
        print(f"\n  Arquivo: {caminho.relative_to(pasta)}")
        print(f"  Linhas: {len(quadro):,}")
        print(f"  Colunas: {list(quadro.columns)}")
        if "level" in quadro.columns:
            print("\n  Distribuicao de `level`:")
            for valor, contagem in quadro["level"].value_counts().sort_index().items():
                print(f"    nivel {valor}: {contagem:,}")
        if "correct" in quadro.columns:
            bem_sucedidos = int(quadro["correct"].sum())
            print(f"\n  Submissoes bem-sucedidas: {bem_sucedidos:,} de {len(quadro):,}")
            print("  (a amostra de 40 sai daqui: um ataque que nao funcionou contra o")
            print("   modelo da competicao nao e caso de ataque)")
        break


def bipia() -> None:
    pasta = ORIGEM / "bipia"
    print()
    print("=" * 78)
    print("BIPIA")
    print("=" * 78)
    if not pasta.exists():
        print("  nao obtido")
        return

    alvos = sorted(pasta.rglob("*attack*.json"))
    if not alvos:
        print("  nenhum arquivo *attack*.json encontrado; arvore:")
        arvore(pasta)
        return

    for caminho in alvos:
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except Exception as erro:  # noqa: BLE001
            print(f"  [{caminho.name}] nao lido: {type(erro).__name__}")
            continue
        print(f"\n  Arquivo: {caminho.relative_to(pasta)}")
        if isinstance(dados, dict):
            total = sum(len(v) if isinstance(v, list) else 1 for v in dados.values())
            print(f"  Categorias: {len(dados)}"
                  f"{conferir('bipia_categorias', len(dados))}")
            print(f"  Cargas: {total}{conferir('bipia_cargas', total)}")
            for chave, valor in dados.items():
                quantidade = len(valor) if isinstance(valor, list) else 1
                print(f"    {quantidade:>4}  {chave}")
        elif isinstance(dados, list):
            print(f"  Itens: {len(dados)}{conferir('bipia_cargas', len(dados))}")
            if dados and isinstance(dados[0], dict):
                print(f"  Campos: {list(dados[0].keys())}")


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--arvore", action="store_true")
    argumentos = analisador.parse_args()

    if not ORIGEM.exists():
        print("conjuntos nao obtidos; rode scripts/obter_conjuntos.py")
        return 1

    if argumentos.arvore:
        for pasta in sorted(p for p in ORIGEM.iterdir() if p.is_dir()):
            print(f"\n{pasta.name}:")
            arvore(pasta)
        return 0

    do_not_answer()
    hackaprompt()
    bipia()

    print()
    print("=" * 78)
    print("Divergencia entre o obtido e a proposta precisa de nota corrigindo o numero,")
    print("e so tem conserto antes do congelamento.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
