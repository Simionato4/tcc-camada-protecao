"""Contrato de entrada e saida da camada.

O mesmo formato vale para os tres pontos de interceptacao. Isso simplifica o
executor: ele monta uma requisicao so e muda apenas o campo `ponto`.

Revisado em 09/11/2026, antes de qualquer regra (Etapa 4, Fase 0; ADR-0027):
- posicao das deteccoes no texto ORIGINAL (RQ-07);
- limite de tamanho do texto e identificador em UUID (RQ-14; ADR-0027, E2);
- campo de erro tecnico na resposta (RQ-10; ADR-0027, E3).
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# ADR-0027, E2: o contexto tem 3 documentos de 150 a 300 tokens (ADR-0007) e a resposta,
# no maximo 400 tokens. O limite da folga e impede requisicao abusiva.
TAMANHO_MAXIMO_TEXTO = 20_000

Ponto = Literal["entrada", "contexto", "saida"]
Condicao = Literal["A", "B", "C", "D"]
Decisao = Literal["encaminhar", "bloquear", "mascarar", "alertar"]
# Categoria propria de falha (RQ-10). Nunca conta como bloqueio correto (ADR-0020, D1):
# com erro, a decisao e `bloquear` (falhar fechado, ADR-0027, E3) e este campo vem preenchido.
Erro = Literal["erro_tecnico"]


class Deteccao(BaseModel):
    """Uma ocorrencia encontrada no texto.

    `posicao` guarda o intervalo [inicio, fim) no texto ORIGINAL, o que a camada
    recebeu, e nao no texto normalizado (RQ-07). A deteccao ocorre sobre o texto
    normalizado, e a normalizacao muda o comprimento; a posicao e convertida pelo mapa
    de posicoes antes de sair da camada. E nesse sistema de coordenadas que o gabarito
    e o protocolo (8.4) medem o mascaramento. `valido` diz se o digito verificador
    conferiu.
    """

    tipo: str
    posicao: tuple[int, int]
    valido: bool


class Requisicao(BaseModel):
    """`id_requisicao` serve a rastreabilidade entre os registros, e nao a autenticacao
    nem a autorizacao: a camada nao confia nele para nada (RQ-14)."""

    ponto: Ponto
    texto: str = Field(max_length=TAMANHO_MAXIMO_TEXTO)
    id_requisicao: UUID
    condicao: Condicao


class Resposta(BaseModel):
    decisao: Decisao
    texto: str
    deteccoes: list[Deteccao] = Field(default_factory=list)
    tempo_ms: float
    # Campos de rastreabilidade: ligam cada registro bruto a configuracao que o
    # gerou. Sem eles, um resultado nao e reproduzivel por terceiros.
    versao_regras: str
    ponto: Ponto
    condicao: Condicao
    erro: Erro | None = None
