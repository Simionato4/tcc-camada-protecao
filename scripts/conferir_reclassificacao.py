"""Confere a regra corrigida contra a revisao manual ja feita (ADR-0017 rev. 2).

O que este script responde: a regra corrigida reproduz, sozinha, os rotulos que foram
atribuidos a mao aos quarenta casos da primeira amostra?

Por que isso nao e ajuste a resultado. A regra corrigida foi escrita a partir do texto
de R1, e nao a partir dos quarenta casos. Estes quarenta sao material de
desenvolvimento — a amostra medida sera **outra**, sorteada depois da correcao — e
servem aqui como verificacao independente de uma regra ja fechada. Divergencia que
aparecer nao autoriza mexer na regra para acertar o caso: autoriza examinar se o erro
esta em R1 ou na implementacao, e registrar o exame.

O CSV de revisao guarda cada caso numa linha so, escapando quebras de linha como `\n`
literal. Essa representacao **nao e o texto classificado**: um `\n` escapado cola um `n`
latino na palavra seguinte e um bloco base64 partido deixa de ser reconhecido. As quebras
sao restauradas antes de classificar. A amostragem nunca sofreu disso, porque classifica o
texto do parquet; so a conferencia sofreria.

Separa dois tipos de divergencia. Contra `classe_revisada` e discordancia de **decisao
humana**, e e o que importa. Contra `classe_automatica` em linha nao revisada e apenas a
regra nova discordando da antiga — o efeito esperado da correcao, nao um problema.

Nao imprime texto de ataque. A saida e identificador e rotulo.

Uso:
    python scripts/conferir_reclassificacao.py conjunto_teste/revisao/hackaprompt_revisao-v1.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classificar_codificacao import CLASSES, classificar  # noqa: E402

DELIMITADOR = ";"
CODIFICACAO_ARQUIVO = "utf-8-sig"

PISTAS_TEXTO = ("texto", "input", "prompt", "user", "conteudo", "conteúdo")
PISTAS_REVISADA = ("revis",)
PISTAS_AUTOMATICA = ("automat", "regra")
PISTAS_ORDEM = ("ordem", "id", "indice", "índice")


def _escolher(cabecalho: list[str], pistas: tuple[str, ...]) -> str | None:
    for pista in pistas:
        for coluna in cabecalho:
            if pista in coluna.strip().lower():
                return coluna
    return None


def _coluna_mais_longa(linhas: list[dict[str, str]], cabecalho: list[str]) -> str:
    medias = {
        coluna: sum(len(linha.get(coluna) or "") for linha in linhas) / max(1, len(linhas))
        for coluna in cabecalho
    }
    return max(medias, key=medias.get)


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument("caminho", type=Path, help="CSV da revisao arquivada")
    analisador.add_argument("--coluna-texto", default=None)
    analisador.add_argument("--coluna-revisada", default=None)
    analisador.add_argument("--coluna-automatica", default=None)
    analisador.add_argument("--coluna-ordem", default=None)
    analisador.add_argument(
        "--manter-escape",
        action="store_true",
        help="nao restaura as quebras de linha escapadas (so para diagnostico)",
    )
    argumentos = analisador.parse_args()

    if not argumentos.caminho.exists():
        print(f"arquivo nao encontrado: {argumentos.caminho}", file=sys.stderr)
        return 2

    with argumentos.caminho.open(encoding=CODIFICACAO_ARQUIVO, newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=DELIMITADOR)
        cabecalho = list(leitor.fieldnames or [])
        linhas = list(leitor)

    if not linhas:
        print("CSV vazio", file=sys.stderr)
        return 2

    col_texto = argumentos.coluna_texto or _escolher(cabecalho, PISTAS_TEXTO) or _coluna_mais_longa(linhas, cabecalho)
    col_revisada = argumentos.coluna_revisada or _escolher(cabecalho, PISTAS_REVISADA)
    col_automatica = argumentos.coluna_automatica or _escolher(cabecalho, PISTAS_AUTOMATICA)
    col_ordem = argumentos.coluna_ordem or _escolher(cabecalho, PISTAS_ORDEM)

    print("colunas do arquivo:", ", ".join(cabecalho))
    print(f"  texto      -> {col_texto}")
    print(f"  revisada   -> {col_revisada}")
    print(f"  automatica -> {col_automatica}")
    print(f"  ordem      -> {col_ordem}")
    print("Confira este mapeamento antes de ler o resultado.\n")

    if col_revisada is None:
        print("sem coluna de classe revisada: nada a conferir", file=sys.stderr)
        return 2

    humanas = 0
    humanas_ok = 0
    divergencias_humanas: list[tuple[str, str, str]] = []
    divergencias_automaticas: list[tuple[str, str, str]] = []
    contagem: dict[str, int] = {classe: 0 for classe in CLASSES}

    for indice, linha in enumerate(linhas, start=1):
        texto = linha.get(col_texto) or ""
        if not argumentos.manter_escape:
            texto = texto.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")

        obtida = classificar(texto)
        contagem[obtida] = contagem.get(obtida, 0) + 1
        identificador = (linha.get(col_ordem) or str(indice)) if col_ordem else str(indice)

        revisada = (linha.get(col_revisada) or "").strip()
        automatica = (linha.get(col_automatica) or "").strip() if col_automatica else ""

        if revisada:
            humanas += 1
            if obtida == revisada:
                humanas_ok += 1
            else:
                divergencias_humanas.append((identificador, revisada, obtida))
        elif automatica and obtida != automatica:
            divergencias_automaticas.append((identificador, automatica, obtida))

    print(f"casos no arquivo:                 {len(linhas)}")
    print(f"decisoes humanas registradas:     {humanas}")
    print(f"reproduzidas pela regra corrigida: {humanas_ok}/{humanas}")
    print(f"linhas nao revistas em que a regra nova discorda da antiga: "
          f"{len(divergencias_automaticas)}\n")

    print("classes produzidas pela regra corrigida:")
    for classe in CLASSES:
        print(f"  {contagem.get(classe, 0):>4}  {classe}")

    if divergencias_humanas:
        print("\nDIVERGENCIAS DE DECISAO HUMANA (identificador | revisao | regra):")
        for identificador, referencia, obtida in divergencias_humanas:
            print(f"  {identificador:>6} | {referencia:28} | {obtida}")
        print(
            "\nCada uma exige exame registrado: o erro esta em R1 ou na implementacao?"
            " Nao ajuste a regra para acertar o caso."
        )

    if divergencias_automaticas:
        print("\nmudancas em relacao a regra antiga, sem revisao humana"
              " (identificador | antiga | corrigida):")
        for identificador, referencia, obtida in divergencias_automaticas:
            print(f"  {identificador:>6} | {referencia:28} | {obtida}")
        print("Estas sao o efeito esperado da correcao, nao divergencias.")

    return 0 if not divergencias_humanas else 1


if __name__ == "__main__":
    raise SystemExit(main())
