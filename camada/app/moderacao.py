"""Condicao D: moderacao de conteudo da OpenAI, chamada pela camada (RF-015; RQ-16;
ADR-0006; ADR-0027, E5).

Usada so na condicao D e so no ponto `entrada`. A camada chama o servico, e nao o
executor, para que o fluxo do assistente seja identico nas quatro condicoes.

Fonte da interface (consulta de 12/11/2026): referencia oficial da OpenAI,
https://developers.openai.com/api/reference/resources/moderations.md -
`POST /moderations`, corpo com `input` e `model`, cabecalho `Authorization: Bearer`;
resposta com `id`, `model` e `results`, e em cada resultado o campo `flagged`.

RQ-16: `omni-moderation-latest` e referencia mutavel. O campo `model` devolvido pela
resposta vai para o registro. **Pendencia declarada:** a referencia nao diz se esse campo
traz a versao datada ou repete o apelido; o exemplo dela repete o apelido. So uma chamada
real mostra o que vem, e ela depende de chave.

O modo simulado e o padrao: nenhuma requisicao sai da maquina, e nada e sinalizado.
A biblioteca padrao basta (`urllib`); a camada nao ganha dependencia nova.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass

URL = "https://api.openai.com/v1/moderations"
MODELO = "omni-moderation-latest"
TEMPO_LIMITE_S = 10


@dataclass(frozen=True)
class Moderacao:
    sinalizado: bool
    modelo: str  # o identificador devolvido pelo servico (RQ-16), ou "simulado"
    simulado: bool


def _chamar_api(texto: str, chave: str) -> dict:
    """Unica funcao que toca a rede. Erro de rede, tempo esgotado e resposta que nao e
    JSON sobem como excecao: quem chama falha fechado (ADR-0027, E3)."""
    requisicao = urllib.request.Request(
        URL,
        data=json.dumps({"model": MODELO, "input": texto}).encode("utf-8"),
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(requisicao, timeout=TEMPO_LIMITE_S) as resposta:  # noqa: S310
        return json.loads(resposta.read().decode("utf-8"))


def moderar(texto: str, *, simulado: bool, chave: str | None) -> Moderacao:
    if simulado:
        return Moderacao(sinalizado=False, modelo="simulado", simulado=True)
    if not chave:
        raise RuntimeError("OPENAI_API_KEY nao definida: a condicao D em modo real exige a chave")
    corpo = _chamar_api(texto, chave)
    # Resposta fora do formato levanta KeyError, IndexError ou TypeError: e erro tecnico.
    sinalizado = corpo["results"][0]["flagged"]
    modelo = corpo["model"]
    if not isinstance(sinalizado, bool) or not isinstance(modelo, str):
        raise ValueError("resposta da moderacao fora do formato esperado")
    return Moderacao(sinalizado=sinalizado, modelo=modelo, simulado=False)
