"""Indexa a base de conhecimento no Qdrant. Tarefa 2.5 e requisito RQ-18.

E **idempotente e destrutivo por desenho**: recria a colecao do zero a cada
execucao. Isso o torna, ao mesmo tempo, o procedimento de indexacao e o
procedimento de restauracao da base entre cenarios — nao ha dois caminhos que
possam divergir.

Uso, com o ambiente de pe:
    docker compose exec recuperador python -m app.indexar
    docker compose exec recuperador python -m app.indexar --verificar
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .indice import COLECAO, DIMENSOES, IndiceQdrant, carregar_documentos, hash_do_estado

BASE = Path(os.getenv("PASTA_BASE_CONHECIMENTO", "/app/base_conhecimento"))


def indexar(indice: IndiceQdrant, documentos: list[dict]) -> None:
    from qdrant_client import models

    indice.cliente.delete_collection(collection_name=COLECAO)
    indice.cliente.create_collection(
        collection_name=COLECAO,
        vectors_config=models.VectorParams(
            size=DIMENSOES, distance=models.Distance.COSINE
        ),
    )
    pontos = [
        models.PointStruct(
            id=i,
            vector=indice.vetorizar(d["texto"]),
            payload={
                "id_documento": d["id_documento"],
                "numero_pedido": d["numero_pedido"],
                "texto": d["texto"],
            },
        )
        for i, d in enumerate(documentos)
    ]
    indice.cliente.upsert(collection_name=COLECAO, points=pontos, wait=True)


def verificar_recuperacao(indice: IndiceQdrant, documentos: list[dict], k: int = 3) -> list[dict]:
    """Confere que cada pergunta pareada traz o seu documento no top-k.

    E a evidencia de conclusao da tarefa 2.5 e a base empirica do ADR-0002: se a
    recuperacao nao for deterministica, os casos de injecao indireta mediriam sorte
    de busca em vez do comportamento da camada.
    """
    import json

    perguntas = json.loads(
        (BASE / "perguntas_pareadas.json").read_text(encoding="utf-8")
    )
    resultados = []
    for pergunta in perguntas:
        achados = indice.buscar(pergunta["pergunta"], k)
        ids = [a.id_documento for a in achados]
        alvo = pergunta["id_documento"]
        resultados.append(
            {
                "id_documento": alvo,
                "pergunta": pergunta["pergunta"],
                "recuperados": ids,
                "posicao": ids.index(alvo) + 1 if alvo in ids else None,
                "no_top_k": alvo in ids,
            }
        )
    return resultados


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--verificar", action="store_true",
                            help="nao reindexa; so confere a recuperacao")
    analisador.add_argument("-k", type=int, default=3)
    argumentos = analisador.parse_args()

    documentos = carregar_documentos(BASE)
    indice = IndiceQdrant()

    if not argumentos.verificar:
        print(f"indexando {len(documentos)} documentos na colecao '{COLECAO}'...")
        indexar(indice, documentos)
        print("indexacao concluida")

    print(f"hash do estado da base: {hash_do_estado(documentos)}")

    resultados = verificar_recuperacao(indice, documentos, argumentos.k)
    acertos = sum(r["no_top_k"] for r in resultados)
    primeiro = sum(r["posicao"] == 1 for r in resultados if r["posicao"])
    print()
    print(f"recuperacao deterministica: {acertos}/{len(resultados)} no top-{argumentos.k}")
    print(f"em primeira posicao:        {primeiro}/{len(resultados)}")

    falhas = [r for r in resultados if not r["no_top_k"]]
    for f in falhas:
        print(f"  FALHOU {f['id_documento']}: recuperou {f['recuperados']}")

    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())
