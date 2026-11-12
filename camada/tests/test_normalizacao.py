"""Normalizacao com mapa de posicoes (Etapa 4, Fase 1, T010; RF-003, RQ-07, `INJ-01`).

Todos os exemplos foram escritos a mao para este arquivo. Nenhum vem do conjunto de
teste congelado nem do conjunto de desenvolvimento. Os caracteres especiais aparecem
por codigo (`\\uXXXX`), nunca colados, para o arquivo ser legivel e conferivel.

Contrato conferido aqui:
- `normalizar(texto)` devolve `texto` normalizado e `mapa`, em que `mapa[i]` e o indice,
  no texto ORIGINAL, do caractere que deu origem a `texto[i]`;
- `intervalo_original(inicio, fim)` converte um intervalo semiaberto do texto
  normalizado no intervalo semiaberto correspondente do texto original.
"""

import unicodedata

import pytest

from camada.app.normalizacao import normalizar

# Um caso por intervalo da RF-003, com os dois limites dos intervalos que tem limites.
INVISIVEIS = [
    ("tag, limite inferior", "\U000E0000"),
    ("tag, meio (TAG LATIN CAPITAL LETTER A)", "\U000E0041"),
    ("tag, limite superior", "\U000E007F"),
    ("seletor de variacao, limite inferior", "︀"),
    ("seletor de variacao, limite superior", "️"),
    ("espaco de largura zero", "​"),
    ("nao-juntor de largura zero", "‌"),
    ("juntor de largura zero", "‍"),
    ("juntor de palavras", "⁠"),
]


@pytest.mark.parametrize("nome,invisivel", INVISIVEIS, ids=[n for n, _ in INVISIVEIS])
def test_remove_cada_intervalo_de_invisivel(nome: str, invisivel: str) -> None:
    resultado = normalizar("ab" + invisivel + "cd")
    assert resultado.texto == "abcd"
    assert resultado.mapa == (0, 1, 3, 4)


def test_texto_sem_nada_a_remover_tem_mapa_identidade() -> None:
    original = "Qual o prazo de entrega do pedido 10001? Não chegou até hoje."
    resultado = normalizar(original)
    assert resultado.texto == original
    assert resultado.mapa == tuple(range(len(original)))


def test_texto_vazio() -> None:
    resultado = normalizar("")
    assert resultado.texto == ""
    assert resultado.mapa == ()


def test_texto_so_de_invisiveis_fica_vazio() -> None:
    resultado = normalizar("​‍️\U000E0041")
    assert resultado.texto == ""
    assert resultado.mapa == ()


def test_invisivel_no_inicio_e_no_fim() -> None:
    resultado = normalizar("​pedido⁠")
    assert resultado.texto == "pedido"
    assert resultado.mapa == (1, 2, 3, 4, 5, 6)


def test_remocao_altera_comprimento_e_o_mapa_aponta_para_o_original() -> None:
    original = "ig​no‌‍re\U000E0041 tu️do"
    resultado = normalizar(original)
    assert resultado.texto == "ignore tudo"
    assert len(resultado.texto) < len(original)
    # Sem variante tipografica no texto, cada caractere normalizado e o proprio original.
    for i, caractere in enumerate(resultado.texto):
        assert original[resultado.mapa[i]] == caractere


def test_mapa_e_crescente_e_tem_o_tamanho_do_texto() -> None:
    resultado = normalizar("a​bﬁc‍１")
    assert len(resultado.mapa) == len(resultado.texto)
    assert list(resultado.mapa) == sorted(resultado.mapa)


# --- Variantes tipograficas (NFKC) -------------------------------------------------


def test_digitos_de_largura_total_viram_digitos_comuns() -> None:
    resultado = normalizar("１２３")  # digitos FULLWIDTH 1, 2, 3
    assert resultado.texto == "123"
    assert resultado.mapa == (0, 1, 2)


def test_um_caractere_que_vira_dois_aponta_duas_vezes_para_a_mesma_origem() -> None:
    resultado = normalizar("ﬁm")  # ligadura LATIN SMALL LIGATURE FI + "m"
    assert resultado.texto == "fim"
    assert resultado.mapa == (0, 0, 1)


def test_acento_decomposto_e_recomposto_e_aponta_para_a_letra_base() -> None:
    resultado = normalizar("até")  # "e" + COMBINING ACUTE ACCENT
    assert resultado.texto == "até"
    assert resultado.mapa == (0, 1, 2)


def test_invisivel_entre_letra_e_acento_nao_impede_a_recomposicao() -> None:
    resultado = normalizar("e​́")
    assert resultado.texto == "é"
    assert resultado.mapa == (0,)


@pytest.mark.parametrize(
    "original",
    [
        "Pedido １０００１ atrasado",
        "conﬁrmação do endereço",
        "ação",  # cedilha e til decompostos
        "① primeiro item",  # CIRCLED DIGIT ONE
    ],
)
def test_resultado_igual_ao_nfkc_do_texto_sem_invisiveis(original: str) -> None:
    assert normalizar(original).texto == unicodedata.normalize("NFKC", original)


# --- Volta para o texto original (RQ-07) -------------------------------------------


def test_cenario_1_da_spec_documento_com_largura_zero_entre_os_digitos() -> None:
    # Sequencia de digitos inventada, sem digito verificador valido: aqui se testa a
    # posicao, nao a validade do documento.
    digitos = "00000000000"
    original = "meu cadastro: " + "​".join(digitos) + ", pode conferir"
    resultado = normalizar(original)

    inicio = resultado.texto.index(digitos)
    fim = inicio + len(digitos)
    inicio_original, fim_original = resultado.intervalo_original(inicio, fim)

    trecho = original[inicio_original:fim_original]
    assert trecho[0] == "0" and trecho[-1] == "0"
    assert trecho.count("​") == len(digitos) - 1
    assert trecho.replace("​", "") == digitos
    assert original[:inicio_original] == "meu cadastro: "
    assert original[fim_original:] == ", pode conferir"


def test_intervalo_original_cobre_o_caractere_de_origem_inteiro() -> None:
    resultado = normalizar("aﬁm")  # normalizado: "afim"
    # So o "i", que veio da ligadura: o intervalo original e a ligadura inteira.
    assert resultado.intervalo_original(2, 3) == (1, 2)


def test_intervalo_original_no_fim_do_texto() -> None:
    resultado = normalizar("x​y​")
    assert resultado.texto == "xy"
    assert resultado.intervalo_original(0, 2) == (0, 3)


@pytest.mark.parametrize("inicio,fim", [(1, 1), (2, 1), (-1, 1), (0, 5)])
def test_intervalo_invalido_e_recusado(inicio: int, fim: int) -> None:
    resultado = normalizar("abcd")
    with pytest.raises(ValueError):
        resultado.intervalo_original(inicio, fim)


def test_e_deterministica() -> None:
    original = "a​bﬁ１"
    assert normalizar(original) == normalizar(original)
