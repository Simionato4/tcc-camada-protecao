"""Contrato de entrada e saida da camada.

O mesmo formato vale para os tres pontos de interceptacao. Isso simplifica o
executor: ele monta uma requisicao so e muda apenas o campo `ponto`.
"""

from typing import Literal

from pydantic import BaseModel, Field

Ponto = Literal["entrada", "contexto", "saida"]
Condicao = Literal["A", "B", "C", "D"]
Decisao = Literal["encaminhar", "bloquear", "mascarar", "alertar"]


class Deteccao(BaseModel):
    """Uma ocorrencia encontrada no texto.

    `posicao` guarda o intervalo [inicio, fim) no texto JA NORMALIZADO, porque e
    sobre ele que a deteccao ocorre. `valido` diz se o digito verificador conferiu.
    """

    tipo: str
    posicao: tuple[int, int]
    valido: bool


class Requisicao(BaseModel):
    ponto: Ponto
    texto: str
    id_requisicao: str
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
