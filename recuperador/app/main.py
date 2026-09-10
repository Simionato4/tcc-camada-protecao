"""Servico de recuperacao — esqueleto da tarefa 2.1.

ESTADO ATUAL: devolve documentos fixos. Nao ha vetorizacao nem consulta ao Qdrant.
O proposito deste esqueleto e permitir que o fluxo do assistente seja montado e
validado de ponta a ponta antes de existir conteudo real, e sem gastar credito.

A busca vetorial entra na tarefa 2.5, apos os 30 documentos serem gerados (2.4).
"""

import os
import time

from fastapi import FastAPI

from .contrato import Documento, Requisicao, Resposta

VERSAO_INDICE = os.getenv("VERSAO_INDICE", "0.0.0-stub")

app = FastAPI(
    title="Servico de recuperacao",
    description="Vetoriza a pergunta e consulta a base de conhecimento.",
    version=VERSAO_INDICE,
)

# Documentos falsos, com a mesma forma dos reais: numero de pedido unico, para que
# o pareamento pergunta-documento do ADR-0002 ja possa ser exercitado no stub.
DOCUMENTOS_FALSOS = [
    Documento(
        id_documento="doc-stub-001",
        numero_pedido="10001",
        texto=(
            "Pedido 10001. Status: em transporte. Transportadora: Rota Sul Logistica. "
            "Previsao de entrega: 21/03/2026. [DOCUMENTO DE TESTE - CONTEUDO FICTICIO]"
        ),
        escore=0.0,
    ),
    Documento(
        id_documento="doc-stub-002",
        numero_pedido="10002",
        texto=(
            "Pedido 10002. Status: entregue. Politica de troca: 30 dias corridos apos "
            "o recebimento. [DOCUMENTO DE TESTE - CONTEUDO FICTICIO]"
        ),
        escore=0.0,
    ),
    Documento(
        id_documento="doc-stub-003",
        numero_pedido="10003",
        texto=(
            "Pedido 10003. Status: aguardando pagamento. Reembolso em ate 10 dias "
            "uteis apos a coleta reversa. [DOCUMENTO DE TESTE - CONTEUDO FICTICIO]"
        ),
        escore=0.0,
    ),
]


@app.post("/buscar", response_model=Resposta)
def buscar(requisicao: Requisicao) -> Resposta:
    inicio = time.perf_counter()
    documentos = DOCUMENTOS_FALSOS[: requisicao.k]
    tempo_ms = (time.perf_counter() - inicio) * 1000
    return Resposta(
        documentos=documentos,
        k=requisicao.k,
        tempo_ms=tempo_ms,
        versao_indice=VERSAO_INDICE,
        ids_recuperados=[d.id_documento for d in documentos],
    )


@app.get("/saude")
def saude() -> dict:
    return {"estado": "ok", "versao_indice": VERSAO_INDICE}
