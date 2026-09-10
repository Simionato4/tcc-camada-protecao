"""Servico de recuperacao.

Parte do assistente de referencia, nao da camada. Fica separado de proposito: a
camada e o objeto avaliado na condicao B, e sua latencia interna e um indicador do
trabalho — acrescentar vetorizacao e consulta ao Qdrant dentro dela tornaria o
`tempo_ms` incomparavel com as demais condicoes (ADR-0011).
"""

import os
import time
from functools import lru_cache

from fastapi import Depends, FastAPI

from .contrato import Documento, Requisicao, Resposta
from .indice import Indice, IndiceFalso, IndiceQdrant

VERSAO_INDICE = os.getenv("VERSAO_INDICE", "0.0.0-stub")
MODO_INDICE = os.getenv("MODO_INDICE", "qdrant")

app = FastAPI(
    title="Servico de recuperacao",
    description="Vetoriza a pergunta e consulta a base de conhecimento.",
    version=VERSAO_INDICE,
)


@lru_cache(maxsize=1)
def obter_indice() -> Indice:
    """O indice e construido uma unica vez.

    Carregar o modelo de embeddings por requisicao acrescentaria segundos a cada
    chamada e distorceria qualquer medicao de tempo.
    """
    if MODO_INDICE == "falso":
        return IndiceFalso()
    return IndiceQdrant()


@app.post("/buscar", response_model=Resposta)
def buscar(requisicao: Requisicao, indice: Indice = Depends(obter_indice)) -> Resposta:
    inicio = time.perf_counter()
    achados = indice.buscar(requisicao.pergunta, requisicao.k)
    tempo_ms = (time.perf_counter() - inicio) * 1000
    documentos = [
        Documento(
            id_documento=a.id_documento,
            numero_pedido=a.numero_pedido,
            texto=a.texto,
            escore=a.escore,
        )
        for a in achados
    ]
    return Resposta(
        documentos=documentos,
        k=requisicao.k,
        tempo_ms=tempo_ms,
        versao_indice=VERSAO_INDICE,
        ids_recuperados=[d.id_documento for d in documentos],
    )


@app.get("/saude")
def saude() -> dict:
    return {"estado": "ok", "versao_indice": VERSAO_INDICE, "modo_indice": MODO_INDICE}
