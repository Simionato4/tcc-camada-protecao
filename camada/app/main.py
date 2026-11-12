"""Camada intermediaria de protecao.

ESTADO ATUAL (Etapa 4, Fase 1, em construcao): tres estagios ligados — normalizacao,
deteccao e decisao — para dado pessoal e para o marcador unico. Injecao, falha fechada e
registro mascarado sao as tarefas seguintes. As regras sao posteriores ao congelamento do conjunto de teste
(`conjunto_teste/CONGELADO.md`, 12/11/2026).

As regras valem so na **condicao B**. Nas condicoes A, C e D a camada encaminha o texto
sem alterar: e isso que torna a diferenca medida atribuivel a camada. (O modo da condicao
D no `/entrada` e a tarefa T026.)

Por que os tres endpoints existem desde a Etapa 0: o fluxo do assistente e variavel de
controle e precisa ser identico nas quatro condicoes. Se os nos HTTP fossem
adicionados so na condicao B, o fluxo mudaria entre condicoes e a diferenca
observada deixaria de ser atribuivel a estrategia de protecao.
"""

import os
import time

from fastapi import FastAPI

from .contrato import Requisicao, Resposta
from .decisao import decidir
from .deteccao import detectar_dados_pessoais, detectar_marcador
from .normalizacao import normalizar
from .registro import registrador

VERSAO_REGRAS = os.getenv("VERSAO_REGRAS", "0.0.0-encaminhamento")


def ler_normalizacao(valor: str) -> bool:
    """Le a configuracao do estagio de normalizacao (RF-012, RQ-12).

    So aceita `ligada` ou `desligada`. Valor desconhecido impede a camada de subir: uma
    ablacao rodada com a configuracao errada sem ninguem perceber invalidaria a medida.
    """
    if valor == "ligada":
        return True
    if valor == "desligada":
        return False
    raise ValueError(f"NORMALIZACAO deve ser 'ligada' ou 'desligada'; recebido: {valor!r}")


NORMALIZACAO_ATIVA = ler_normalizacao(os.getenv("NORMALIZACAO", "ligada"))

# Marcador unico do prompt de sistema (`assistente/prompt_sistema.md`, congelado). Nao e
# segredo (RQ-01): e instrumento de medicao do criterio `CTX-02`.
MARCADOR_PADRAO = "CANARIO-TCC-2DEFEC2A9B0F"


def ler_marcador(valor: str) -> str:
    """Le o marcador unico. Vazio ou curto impede a camada de subir: sem ele a regra do
    `CTX-02` ficaria desligada em silencio, e um valor curto casaria com texto comum."""
    valor = valor.strip()
    if len(valor) < 16:
        raise ValueError("MARCADOR vazio ou curto demais (minimo de 16 caracteres)")
    return valor


MARCADOR = ler_marcador(os.getenv("MARCADOR", MARCADOR_PADRAO))

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

    if requisicao.condicao != "B":
        # Condicoes A, C e D: passagem pura.
        decisao, texto, deteccoes = "encaminhar", requisicao.texto, []
    else:
        # Estagio 1: normalizacao, com o mapa de posicoes para o texto original.
        normalizado = normalizar(requisicao.texto, ativa=NORMALIZACAO_ATIVA)
        # Estagio 2: deteccao sobre o texto normalizado; posicoes ja no original.
        encontradas = detectar_dados_pessoais(normalizado)
        marcadores = (
            detectar_marcador(normalizado, MARCADOR) if requisicao.ponto == "saida" else []
        )
        # Estagio 3: decisao (bloqueio ou mascaramento) sobre o texto ORIGINAL.
        resultado = decidir(requisicao.ponto, requisicao.texto, encontradas, marcadores)
        decisao, texto, deteccoes = resultado.decisao, resultado.texto, resultado.deteccoes

    tempo_ms = (time.perf_counter() - inicio) * 1000
    return decisao, texto, deteccoes, tempo_ms


def _atender(requisicao: Requisicao) -> Resposta:
    decisao, texto, deteccoes, tempo_ms = processar(requisicao)

    registrador.requisicao_processada(
        id_requisicao=str(requisicao.id_requisicao),
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
    return {
        "estado": "ok",
        "versao_regras": VERSAO_REGRAS,
        "normalizacao": "ligada" if NORMALIZACAO_ATIVA else "desligada",
    }
