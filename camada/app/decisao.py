"""Estagio 3 da camada: decisao e mascaramento (RF-005, RF-007; `PII-01`, `PII-02`,
`CTX-02`).

Marcador unico na `saida` (decisao do autor, 12/11/2026): **bloquear** a resposta inteira
e devolver texto vazio. Mascarar so o marcador esconderia a evidencia do vazamento e
entregaria o resto do conteudo oculto. O marcador e verificado antes do mascaramento.

Politica por ponto, para dado pessoal (decisoes do autor, 12/11/2026):

| Ponto | Com dado pessoal detectado |
|---|---|
| `contexto` | `mascarar`: o dado da base nao chega ao modelo |
| `saida` | `mascarar`: o dado nao chega ao usuario |
| `entrada` | `encaminhar`, com as deteccoes informadas: o cliente esta fornecendo o proprio dado, e mascarar impediria o atendimento |

O mascaramento e feito no texto **original**, pelas posicoes das deteccoes (RQ-07): so o
trecho do dado e trocado, e o resto sai como veio. No lugar do dado entra o rotulo do
tipo, entre colchetes. O trecho coberto e a ocorrencia inteira (ADR-0020, D3).
"""

from __future__ import annotations

from dataclasses import dataclass

from .contrato import Decisao, Deteccao, Ponto

MARCAS: dict[str, str] = {
    "cpf": "[CPF]",
    "cnpj": "[CNPJ]",
    "pis": "[PIS]",
    "cns": "[CNS]",
    "titulo": "[TITULO]",
    "telefone": "[TELEFONE]",
    "email": "[EMAIL]",
}

_PONTOS_QUE_MASCARAM: tuple[Ponto, ...] = ("contexto", "saida")


@dataclass(frozen=True)
class Resultado:
    decisao: Decisao
    texto: str
    deteccoes: list[Deteccao]


def mascarar(texto: str, deteccoes: list[Deteccao]) -> str:
    """Troca cada trecho detectado pela marca do seu tipo.

    As deteccoes chegam em ordem e sem sobreposicao (garantia da deteccao). Tipo sem
    marca levanta `KeyError`: um dado nao pode sair em claro por falta de rotulo, e a
    falha vira erro tecnico com bloqueio (ADR-0027, E3).
    """
    partes: list[str] = []
    cursor = 0
    for deteccao in deteccoes:
        inicio, fim = deteccao.posicao
        partes.append(texto[cursor:inicio])
        partes.append(MARCAS[deteccao.tipo])
        cursor = fim
    partes.append(texto[cursor:])
    return "".join(partes)


def decidir(
    ponto: Ponto,
    texto: str,
    deteccoes: list[Deteccao],
    marcadores: list[Deteccao] | None = None,
) -> Resultado:
    """Aplica a politica do ponto ao texto original.

    `deteccoes` sao as de dado pessoal; `marcadores`, as do marcador unico. Com marcador
    na saida, bloqueia e nao devolve nada do texto.
    """
    if marcadores and ponto == "saida":
        todas = sorted(marcadores + deteccoes, key=lambda d: d.posicao)
        return Resultado("bloquear", "", todas)
    if deteccoes and ponto in _PONTOS_QUE_MASCARAM:
        return Resultado("mascarar", mascarar(texto, deteccoes), deteccoes)
    return Resultado("encaminhar", texto, deteccoes)
