"""Servico do modelo de linguagem.

Existe por uma razao metodologica, e nao por conveniencia: **nenhum modulo do
projeto chama o modelo fora de `executor/cliente_modelo.py`**, e toda chamada passa
antes pelo `GuardaOrcamento`. Se o fluxo do assistente chamasse a API diretamente por
um no HTTP, o gasto ocorreria fora do guarda, fora do contador e fora do teto — e a
restricao inviolavel de orcamento deixaria de significar alguma coisa.

Este servico embrulha o mesmo cliente que o executor usa, de modo que as chamadas do
fluxo e as do executor entrem no mesmo livro-caixa.
"""

import hashlib
import os
import time
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI

from executor.cliente_modelo import ClienteModelo
from executor.orcamento import GuardaOrcamento, OrcamentoExcedido

from .contrato import Requisicao, Resposta
from .prompt import carregar_prompt

CAMINHO_PROMPT = Path(os.getenv("CAMINHO_PROMPT", "/app/assistente/prompt_sistema.md"))

app = FastAPI(
    title="Servico do modelo",
    description="Unico ponto do fluxo autorizado a chamar o modelo de linguagem.",
)


@lru_cache(maxsize=1)
def obter_prompt() -> tuple[str, str]:
    texto = carregar_prompt(CAMINHO_PROMPT)
    return texto, hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


@lru_cache(maxsize=1)
def obter_cliente() -> ClienteModelo:
    return ClienteModelo(GuardaOrcamento())


@app.post("/gerar", response_model=Resposta)
def gerar(requisicao: Requisicao) -> Resposta:
    sistema, hash_prompt = obter_prompt()
    cliente = obter_cliente()
    inicio = time.perf_counter()
    try:
        resultado = cliente.responder(sistema=sistema, mensagem=requisicao.mensagem)
    except OrcamentoExcedido as erro:
        # Estourar o teto e condicao de parada do experimento, e nao um erro comum:
        # 503 sinaliza que o servico se recusa a continuar, e o executor deve parar.
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail=f"orcamento: {erro}") from erro
    tempo_ms = (time.perf_counter() - inicio) * 1000
    return Resposta(
        resposta=resultado.texto,
        tokens_entrada=resultado.tokens_entrada,
        tokens_saida=resultado.tokens_saida,
        usd=resultado.usd,
        simulado=resultado.simulado,
        modelo=cliente.modelo,
        tempo_ms=tempo_ms,
        hash_prompt=hash_prompt,
    )


@app.get("/saude")
def saude() -> dict:
    cliente = obter_cliente()
    _, hash_prompt = obter_prompt()
    return {
        "estado": "ok",
        "modelo": cliente.modelo,
        "simulado": cliente.simulado,
        "hash_prompt": hash_prompt,
        "consumo": cliente.guarda.consumo.como_dicionario(),
        "restante": cliente.guarda.restante(),
    }
