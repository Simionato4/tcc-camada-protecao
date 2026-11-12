"""Decodificacao para analise (Etapa 4, T020; RF-006, RQ-08; ADR-0027, E1).

A camada decodifica para **analisar**; o que ela encaminha e sempre o texto original.
Tres origens: base64, codificacao percentual e texto escondido em bloco de tag
(U+E0020 a U+E007E). Ate 2 niveis; resultado de cada nivel limitado ao tamanho maximo
da entrada.

Frases escritas para este arquivo; nenhuma vem do conjunto congelado nem do de
desenvolvimento.
"""

import base64
from urllib.parse import quote

import pytest

from camada.app.contrato import TAMANHO_MAXIMO_TEXTO
from camada.app.decodificacao import vistas_decodificadas
from camada.app.normalizacao import normalizar

FRASE = "Quero saber o horario de funcionamento da loja."


def b64(texto: str) -> str:
    return base64.b64encode(texto.encode("utf-8")).decode("ascii")


def em_tags(texto: str) -> str:
    return "".join(chr(0xE0000 + ord(c)) for c in texto)


def vistas(texto: str, **opcoes):
    return vistas_decodificadas(texto, normalizar(texto), **opcoes)


def resumo(texto: str, **opcoes) -> list[tuple[str, int, str]]:
    return [(v.origem, v.nivel, v.texto) for v in vistas(texto, **opcoes)]


# --- Um nivel -------------------------------------------------------------------------


def test_base64() -> None:
    codificado = b64(FRASE)
    texto = f"Ola, tudo bem? {codificado}"
    (vista,) = vistas(texto)
    assert (vista.origem, vista.nivel, vista.texto) == ("base64", 1, FRASE)
    assert texto[vista.posicao[0] : vista.posicao[1]] == codificado


def test_base64_com_acentos() -> None:
    frase = "Informação sobre a devolução, por favor."
    assert resumo(b64(frase)) == [("base64", 1, frase)]


def test_codificacao_percentual() -> None:
    codificado = quote(FRASE)
    texto = f"veja: {codificado}"
    (vista,) = vistas(texto)
    assert (vista.origem, vista.nivel, vista.texto) == ("percentual", 1, FRASE)
    assert texto[vista.posicao[0] : vista.posicao[1]] == codificado


def test_bloco_de_tag() -> None:
    escondido = em_tags(FRASE)
    texto = f"Ola, tudo bem? {escondido}"
    (vista,) = vistas(texto)
    assert (vista.origem, vista.nivel, vista.texto) == ("bloco_de_tag", 1, FRASE)
    assert texto[vista.posicao[0] : vista.posicao[1]] == escondido


def test_base64_com_invisiveis_no_meio_e_decodificado_depois_da_normalizacao() -> None:
    codificado = "​".join(b64(FRASE))
    (vista,) = vistas(f"veja {codificado} obrigado")
    assert vista.texto == FRASE
    assert f"veja {codificado} obrigado"[vista.posicao[0] : vista.posicao[1]] == codificado


# --- Dois niveis, e nao mais ----------------------------------------------------------


def test_base64_dentro_de_base64() -> None:
    assert resumo(b64(b64(FRASE))) == [("base64", 1, b64(FRASE)), ("base64", 2, FRASE)]


def test_percentual_dentro_de_base64() -> None:
    assert resumo(b64(quote(FRASE))) == [("base64", 1, quote(FRASE)), ("percentual", 2, FRASE)]


def test_base64_dentro_de_bloco_de_tag() -> None:
    assert resumo(em_tags(b64(FRASE))) == [("bloco_de_tag", 1, b64(FRASE)), ("base64", 2, FRASE)]


def test_terceiro_nivel_nao_e_decodificado() -> None:
    tres = b64(b64(b64(FRASE)))
    assert [(v.nivel, v.texto) for v in vistas(tres)] == [(1, b64(b64(FRASE))), (2, b64(FRASE))]


def test_posicao_do_segundo_nivel_e_a_do_trecho_externo() -> None:
    externo = b64(b64(FRASE))
    texto = f"olha {externo} isso"
    for vista in vistas(texto):
        assert texto[vista.posicao[0] : vista.posicao[1]] == externo


# --- Limite de tamanho ----------------------------------------------------------------


def test_limite_padrao_e_o_tamanho_maximo_da_entrada() -> None:
    longo = "a " * 60
    assert resumo(b64(longo), limite=TAMANHO_MAXIMO_TEXTO) == resumo(b64(longo))


def test_resultado_acima_do_limite_e_descartado() -> None:
    assert resumo(b64(FRASE), limite=len(FRASE)) == [("base64", 1, FRASE)]
    assert resumo(b64(FRASE), limite=len(FRASE) - 1) == []


def test_limite_vale_em_cada_nivel() -> None:
    # O primeiro nivel (base64 da frase) e maior que a frase: com o limite no tamanho da
    # frase, o primeiro nivel ja e descartado e o segundo nunca e alcancado.
    assert resumo(b64(b64(FRASE)), limite=len(FRASE)) == []


# --- O que nao e conteudo codificado ----------------------------------------------------


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "Qual o prazo de entrega do pedido 10001?",
        "d41d8cd98f00b204e9800998ecf8427e",  # resumo MD5: caracteres de base64, bytes sem texto
        "1234567890123456",  # numero longo
        "Otorrinolaringologista",  # palavra longa
        "desconto de 10% e frete de 5% hoje",  # sinal de porcentagem comum
        "https://example.com/produto?id=10&cor=azul",
        "A" * 40,
    ],
)
def test_sem_vista(texto: str) -> None:
    assert vistas(texto) == []


def test_e_deterministica() -> None:
    texto = f"{b64(FRASE)} e {quote(FRASE)}"
    assert vistas(texto) == vistas(texto)
