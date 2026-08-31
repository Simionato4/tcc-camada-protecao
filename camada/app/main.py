"""Camada intermediaria de protecao - esqueleto da Etapa 0.

ESTADO ATUAL: encaminhamento puro. Nenhuma regra de deteccao existe neste
repositorio, e nenhuma pode existir antes do congelamento do conjunto de teste
(Etapa 3). Os arquivos normalizacao.py, deteccao.py e decisao.py sao criados
somente depois que CONGELADO.md estiver datado e com hash.

Por que os tres endpoints ja existem: o fluxo do assistente e variavel de
controle e precisa ser identico nas quatro condicoes. Se os nos HTTP fossem
adicionados so na condicao B, o fluxo mudaria entre condicoes e a diferenca
observada deixaria de ser atribuivel a estrategia de protecao.
"""

import os
import time

from fastapi import FastAPI

from app.contrato import Requisicao, Resposta
from app.registro import registrador

VERSAO_REGRAS = os.getenv("VERSAO_REGRAS", "0.0.0-encaminhamento")

app = FastAPI(
    title="Camada intermediaria de protecao",
    description="Interceptacao de entrada, contexto e saida de um assistente com LLM.",
    version=VERSAO_REGRAS,
)


def processar(requisicao: Requisicao) -> tuple[str, str, list, float]:
    """Aplica a politica ao texto e devolve (decisao, texto, deteccoes, tempo_ms).

    O cronometro envolve apenas o processamento. Serializacao HTTP e rede ficam
    de fora, porque a metrica de latencia definida no protocolo e o tempo interno
    da camada.
    """
    inicio = time.perf_counter()

    # Etapa 0: passagem pura, identica nas quatro condicoes.
    decisao = "encaminhar"
    texto = requisicao.texto
    deteccoes: list = []

    tempo_ms = (time.perf_counter() - inicio) * 1000
    return decisao, texto, deteccoes, tempo_ms


def _atender(requisicao: Requisicao) -> Resposta:
    decisao, texto, deteccoes, tempo_ms = processar(requisicao)

    registrador.requisicao_processada(
        id_requisicao=requisicao.id_requisicao,
        ponto=requisicao.ponto,
        condicao=requisicao.condicao,
        texto_entrada=requisicao.texto,
        texto_saida=texto,
        decisao=decisao,
        quantidade_deteccoes=len(deteccoes),
        tempo_ms=tempo_ms,
        versao_regras=VERSAO_REGRAS,
    )

    return Resposta(
        decisao=decisao,
        texto=texto,
        deteccoes=deteccoes,
        tempo_ms=tempo_ms,
        versao_regras=VERSAO_REGRAS,
        ponto=requisicao.ponto,
        condicao=requisicao.condicao,
    )


@app.post("/entrada", response_model=Resposta)
def interceptar_entrada(requisicao: Requisicao) -> Resposta:
    """Mensagem do usuario, antes de alcancar o assistente."""
    return _atender(requisicao)


@app.post("/contexto", response_model=Resposta)
def interceptar_contexto(requisicao: Requisicao) -> Resposta:
    """Conteudo recuperado da base, antes de compor o contexto."""
    return _atender(requisicao)


@app.post("/saida", response_model=Resposta)
def interceptar_saida(requisicao: Requisicao) -> Resposta:
    """Resposta gerada, antes de retornar ao usuario."""
    return _atender(requisicao)


@app.get("/saude")
def saude() -> dict:
    return {"estado": "ok", "versao_regras": VERSAO_REGRAS}
