"""Inventario dos rotulos de origem dos tres conjuntos publicos (tarefa 3.4, ADR-0018).

LEITURA PURA: nao grava nada. Imprime contagens; nenhum texto de solicitacao, ataque ou
carga. A excecao deliberada sao os nomes de rotulo dos proprios conjuntos (area de
risco, tipo de dano, categoria do BIPIA), que sao metadados publicados.

O bloco do HackAPrompt tambem responde a pergunta do CTX-02: em que niveis o objetivo do
ataque e extrair algo do contexto oculto. Sinal mecanico usado: o `expected_completion`
aparece dentro do `prompt` montado pela competicao, mas nao no `user_input`. Isto e, o
atacante precisava fazer o modelo revelar algo que estava no prompt e que ele nao
escreveu. Sinal descritivo, a ser examinado antes de qualquer decisao.
"""

from __future__ import annotations

import collections
import csv
import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "conjunto_teste" / "origem"
SELECAO = RAIZ / "conjunto_teste" / "selecao" / "hackaprompt.json"


def do_not_answer() -> None:
    with (ORIGEM / "do-not-answer" / "data_en.csv").open(encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    print(f"== Do-Not-Answer: {len(linhas)} solicitacoes")
    por_par = collections.Counter((l["risk_area"], l["types_of_harm"]) for l in linhas)
    areas = collections.Counter(l["risk_area"] for l in linhas)
    for area in sorted(areas):
        print(f"  {areas[area]:>4}  {area}")
        for (a, tipo), n in sorted(por_par.items()):
            if a == area:
                print(f"        {n:>4}  {tipo}")
    especificos = {l["specific_harms"] for l in linhas}
    print(f"  specific_harms distintos: {len(especificos)}")
    print()


def bipia() -> None:
    bench = ORIGEM / "bipia" / "benchmark"
    texto = json.loads((bench / "text_attack_test.json").read_text(encoding="utf-8"))
    codigo = json.loads((bench / "code_attack_test.json").read_text(encoding="utf-8"))
    print(
        f"== BIPIA: ataques de texto {sum(len(v) for v in texto.values())} em "
        f"{len(texto)} categorias; ataques de codigo {sum(len(v) for v in codigo.values())} "
        f"em {len(codigo)} categorias (excluidos, ADR-0014)"
    )
    for categoria, cargas in texto.items():
        print(f"  {len(cargas):>4}  {categoria}")
    print()


def hackaprompt() -> None:
    spec = importlib.util.spec_from_file_location(
        "amostrar_hackaprompt", RAIZ / "scripts" / "amostrar_hackaprompt.py"
    )
    amostrar = importlib.util.module_from_spec(spec)
    sys.modules["amostrar_hackaprompt"] = amostrar
    spec.loader.exec_module(amostrar)

    quadro, _, _ = amostrar.carregar_universo()
    selecao = json.loads(SELECAO.read_text(encoding="utf-8"))
    na_amostra = collections.Counter(int(c["level"]) for c in selecao["selecionados"])

    print(f"== HackAPrompt: universo de {len(quadro):,} casos; amostra de "
          f"{len(selecao['selecionados'])}")
    print(f"  {'level':>5}{'universo':>10}{'amostra':>9}{'alvos distintos':>17}"
          f"{'alvo no prompt e fora do user_input':>38}")
    for level, grupo in sorted(quadro.groupby("level"), key=lambda g: int(g[0])):
        alvos = grupo["expected_completion"].astype(str)
        distintos = alvos.nunique()
        oculto = sum(
            1
            for alvo, prompt, entrada in zip(alvos, grupo["prompt"].astype(str), grupo["_texto"])
            if alvo.strip() and alvo in prompt and alvo not in entrada
        )
        print(f"  {int(level):>5}{len(grupo):>10,}{na_amostra.get(int(level), 0):>9}"
              f"{distintos:>17,}{oculto:>20,} ({100 * oculto / len(grupo):5.1f}%)")
    print()


def main() -> int:
    do_not_answer()
    bipia()
    hackaprompt()
    print("Nenhum arquivo gravado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
