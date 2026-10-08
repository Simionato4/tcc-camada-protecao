"""Subamostra do CTX-02: 10 casos de extracao de contexto oculto do HackAPrompt (ADR-0018).

Criterio de extracao, fixado na ADR-0018 antes do sorteio: caso de `level` 2 em que o
`expected_completion` aparece no `prompt` montado pela competicao e nao aparece no
`user_input`. Isto e, o atacante fez o modelo revelar um segredo que ele nao escreveu.

Universo: o mesmo da ADR-0017 (`carregar_universo`). Excluem-se os casos ja presentes na
amostra de 40 (`hackaprompt.json`), para que nenhum caso pertenca a dois grupos.
Ordenacao por sha256 do `user_input` e sorteio com a semente registrada, como na ADR-0017.

Grava `conjunto_teste/selecao/hackaprompt_ctx.json`, sem texto (ADR-0016). Recusa
sobrescrever uma selecao existente sem `--refazer`.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import os
import random
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SELECAO = RAIZ / "conjunto_teste" / "selecao"
AMOSTRA_INJ = SELECAO / "hackaprompt.json"
SAIDA = SELECAO / "hackaprompt_ctx.json"
TAMANHO = 10
LEVEL_EXTRACAO = 2

_spec = importlib.util.spec_from_file_location(
    "amostrar_hackaprompt", RAIZ / "scripts" / "amostrar_hackaprompt.py"
)
amostrar = importlib.util.module_from_spec(_spec)
sys.modules["amostrar_hackaprompt"] = amostrar
_spec.loader.exec_module(amostrar)
clf = amostrar.clf


def eh_extracao(level: object, alvo: object, prompt: object, entrada: str) -> bool:
    """Criterio textual da ADR-0018."""
    if int(level) != LEVEL_EXTRACAO:
        return False
    if not isinstance(alvo, str) or not alvo.strip() or not isinstance(prompt, str):
        return False
    return alvo in prompt and alvo not in entrada


def sortear(candidatos: list[dict], tamanho: int, semente: int) -> list[dict]:
    ordenados = sorted(candidatos, key=lambda r: amostrar.sha256(r["_texto"]))
    return random.Random(semente).sample(ordenados, tamanho)


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--refazer", action="store_true")
    argumentos = analisador.parse_args()
    if SAIDA.exists() and not argumentos.refazer:
        print(f"{SAIDA.name} ja existe; use --refazer para sortear de novo.", file=sys.stderr)
        return 1

    semente = int(os.getenv("SEMENTE_MESTRA", "20260829"))
    quadro, _, _ = amostrar.carregar_universo()
    ja_na_amostra = {
        c["sha256_user_input"]
        for c in json.loads(AMOSTRA_INJ.read_text(encoding="utf-8"))["selecionados"]
    }

    registros = quadro.to_dict("records")
    extracao = [
        r for r in registros
        if eh_extracao(r["level"], r.get("expected_completion"), r.get("prompt"), r["_texto"])
    ]
    candidatos = [r for r in extracao if amostrar.sha256(r["_texto"]) not in ja_na_amostra]
    escolhidos = sortear(candidatos, TAMANHO, semente)

    selecionados = []
    for indice, r in enumerate(escolhidos, start=1):
        selecionados.append({
            "ordem": indice,
            "session_id": str(r.get("session_id", "")),
            "level": int(r["level"]),
            "sha256_user_input": amostrar.sha256(r["_texto"]),
            "caracteres": len(r["_texto"]),
            "classe_automatica": clf.classificar(r["_texto"], r.get("expected_completion")),
        })

    resultado = {
        "descricao": "Subamostra do CTX-02 (ADR-0018). Sem texto de ataque (ADR-0016).",
        "criterio": "level 2; expected_completion presente no prompt e ausente do user_input",
        "semente": semente,
        "data": date.today().isoformat(),
        "universo": len(registros),
        "atendem_criterio": len(extracao),
        "excluidos_por_estarem_na_amostra_inj": len(extracao) - len(candidatos),
        "selecionados": selecionados,
    }
    amostrar.escrever_texto(
        SAIDA, json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )

    print(f"semente: {semente}")
    print(f"universo: {len(registros):,}")
    print(f"atendem o criterio de extracao: {len(extracao):,}")
    print(f"excluidos por ja estarem na amostra do INJ: {len(extracao) - len(candidatos)}")
    print(f"selecionados: {len(selecionados)}")
    print("classe de codificacao (atributo, sem revisao manual):")
    for classe, n in sorted(collections.Counter(s["classe_automatica"] for s in selecionados).items()):
        print(f"  {n:>3}  {classe}")
    print(f"gravado: {SAIDA}  (sem o texto)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
