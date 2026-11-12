"""Camada intermediaria de protecao.

ESTADO ATUAL (Etapa 4, Fase 1, em construcao): tres estagios ligados — normalizacao,
deteccao e decisao — para dado pessoal, marcador unico e injecao de instrucao, com falha
fechada e registro sem texto. As regras sao posteriores ao congelamento do conjunto de teste
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

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .contrato import Requisicao, Resposta
from .decisao import decidir
from .deteccao import detectar_dados_pessoais, detectar_marcador
from .injecao import detectar_injecao
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


@app.exception_handler(RequestValidationError)
async def requisicao_invalida(_requisicao: Request, erro: RequestValidationError) -> JSONResponse:
    """Recusa por validacao (HTTP 422) **sem devolver o conteudo recebido**.

    O tratamento padrao do FastAPI copia a entrada invalida para a resposta. Isso tem dois
    problemas: devolve em claro o texto recusado (que pode trazer dado pessoal), e quebra
    com erro 500 quando o texto nao e Unicode valido (substituto UTF-16 solto), porque a
    propria resposta de erro deixa de ser serializavel. Aqui a resposta traz so o tipo, o
    campo e a mensagem de cada erro.
    """
    detalhes = [
        {"type": e.get("type"), "loc": list(e.get("loc", ())), "msg": e.get("msg")}
        for e in erro.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": detalhes})


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
        injecoes, codificados = (
            detectar_injecao(requisicao.texto, normalizado)
            if requisicao.ponto in ("entrada", "contexto")
            else ([], [])
        )
        # Estagio 3: decisao (bloqueio, mascaramento ou alerta) sobre o texto ORIGINAL.
        resultado = decidir(
            requisicao.ponto, requisicao.texto, encontradas, marcadores, injecoes, codificados
        )
        decisao, texto, deteccoes = resultado.decisao, resultado.texto, resultado.deteccoes

    tempo_ms = (time.perf_counter() - inicio) * 1000
    return decisao, texto, deteccoes, tempo_ms


def _atender(requisicao: Requisicao) -> Resposta:
    """Processa, registra e responde. **Falha fechada** (RF-010; RQ-10; ADR-0027, E3):
    qualquer erro na analise ou no registro vira `bloquear`, com texto vazio e
    `erro = erro_tecnico`. Nunca encaminhamento sem inspecao, nunca erro HTTP 500."""
    normalizacao = "ligada" if NORMALIZACAO_ATIVA else "desligada"
    inicio = time.perf_counter()
    try:
        decisao, texto, deteccoes, tempo_ms = processar(requisicao)
        erro = None
        _registrar(requisicao, texto, decisao, deteccoes, erro, normalizacao, tempo_ms)
    except Exception:  # noqa: BLE001 - falhar fechado vale para qualquer erro
        decisao, texto, deteccoes, erro = "bloquear", "", [], "erro_tecnico"
        tempo_ms = (time.perf_counter() - inicio) * 1000
        try:
            _registrar(requisicao, texto, decisao, deteccoes, erro, normalizacao, tempo_ms)
        except Exception:  # noqa: BLE001 - sem registro, a resposta ainda e o bloqueio
            pass

    return Resposta(
        decisao=decisao,
        texto=texto,
        deteccoes=deteccoes,
        tempo_ms=tempo_ms,
        versao_regras=VERSAO_REGRAS,
        ponto=requisicao.ponto,
        condicao=requisicao.condicao,
        erro=erro,
    )


def _registrar(
    requisicao: Requisicao,
    texto_saida: str,
    decisao: str,
    deteccoes: list,
    erro: str | None,
    normalizacao: str,
    tempo_ms: float,
) -> None:
    registrador.requisicao_processada(
        id_requisicao=str(requisicao.id_requisicao),
        ponto=requisicao.ponto,
        condicao=requisicao.condicao,
        texto_entrada=requisicao.texto,
        texto_saida=texto_saida,
        decisao=decisao,
        # So tipo e posicao: o trecho detectado nunca vai para o registro (`PII-03`).
        deteccoes=[{"tipo": d.tipo, "posicao": list(d.posicao)} for d in deteccoes],
        erro=erro,
        normalizacao=normalizacao,
        tempo_ms=tempo_ms,
        versao_regras=VERSAO_REGRAS,
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
