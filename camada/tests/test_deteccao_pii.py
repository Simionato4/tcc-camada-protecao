"""Deteccao de dado pessoal no texto (Etapa 4, T015; RF-004, RQ-07, `PII-01`).

Todos os textos e numeros foram escritos para este arquivo; nenhum vem do corpus congelado
nem do conjunto de desenvolvimento. Os numeros validos sao os de `test_documentos.py`
(exemplos publicados e contas feitas a mao) e os enderecos usam dominios reservados para
exemplo (`example.com`, `example.org`).

Regras conferidas (aprovadas pelo autor em 12/11/2026):
1. o candidato e a sequencia inteira de digitos ligados por um separador simples
   (espaco, ponto, hifen, barra); nunca um pedaco dela;
2. sequencia colada em virgula ou dois-pontos seguidos de digito e valor ou horario;
3. sequencia colada em letra maiuscula ou digito nao vale; em minuscula, vale;
4. colisao em 11 digitos: rotulo por prioridade CPF, PIS, celular;
5. a posicao devolvida e no texto ORIGINAL.
"""

import pytest

from camada.app.deteccao import detectar_dados_pessoais
from camada.app.documentos import celular_valido, cpf_valido, pis_valido
from camada.app.normalizacao import normalizar


def achar(texto: str, normalizacao: bool = True) -> list[tuple[str, str]]:
    """Devolve (tipo, trecho do texto ORIGINAL) de cada deteccao, na ordem do texto."""
    deteccoes = detectar_dados_pessoais(normalizar(texto, ativa=normalizacao))
    return [(d.tipo, texto[d.posicao[0] : d.posicao[1]]) for d in deteccoes]


# --- Os sete tipos, nos tres formatos de mascara ------------------------------------

CASOS_DE_FORMATO = [
    # (tipo, como aparece no texto)
    ("cpf", "123.456.789-09"),  # completa
    ("cpf", "12345678909"),  # ausente
    ("cpf", "123.456789-09"),  # parcial
    ("cpf", "123456.78909"),  # parcial
    ("cpf", "123 456 789 09"),  # espacos
    ("cnpj", "18.781.203/0001-28"),
    ("cnpj", "18781203000128"),
    ("cnpj", "18.781203/000128"),
    ("cnpj", "18 781 203 0001 28"),
    ("cnpj", "12.ABC.345/01DE-35"),  # alfanumerico, completa
    ("cnpj", "12ABC34501DE35"),  # alfanumerico, ausente
    ("cnpj", "12ABC.345/01DE35"),  # alfanumerico, parcial
    ("cnpj", "12 ABC 345 01DE 35"),  # alfanumerico, espacos
    ("pis", "120.54789.01-3"),
    ("pis", "12054789013"),
    ("pis", "120.5478901-3"),
    ("pis", "120 54789 01 3"),
    ("cns", "700 0000 0000 0005"),
    ("cns", "700000000000005"),
    ("cns", "7000000 0000 0005"),
    ("titulo", "1023 8501 0671"),
    ("titulo", "102385010671"),
    ("titulo", "10238501 0671"),
    ("telefone", "(11) 91234-5678"),
    ("telefone", "(11)91234-5678"),
    ("telefone", "11912345678"),
    ("telefone", "11 91234 5678"),
    ("telefone", "11 91234-5678"),
    ("telefone", "+55 11 91234-5678"),
    ("telefone", "5511912345678"),
    ("email", "fulano.teste@example.com"),
    ("email", "fulano_teste9@example.org"),
    ("email", "fulano@sub.example.com"),
]


@pytest.mark.parametrize("tipo,valor", CASOS_DE_FORMATO)
def test_detecta_no_meio_do_texto_com_a_posicao_exata(tipo: str, valor: str) -> None:
    assert achar(f"Segue o dado: {valor}, pode conferir.") == [(tipo, valor)]


@pytest.mark.parametrize("tipo,valor", CASOS_DE_FORMATO)
def test_detecta_no_inicio_e_no_fim_do_texto(tipo: str, valor: str) -> None:
    assert achar(valor) == [(tipo, valor)]
    assert achar(f"{valor} e o dado. Repetindo: {valor}") == [(tipo, valor), (tipo, valor)]


@pytest.mark.parametrize("tipo,valor", CASOS_DE_FORMATO)
def test_ponto_final_depois_do_dado_fica_fora_da_posicao(tipo: str, valor: str) -> None:
    assert achar(f"O dado e {valor}.") == [(tipo, valor)]


# --- O que nao e dado pessoal -------------------------------------------------------

NAO_DETECTA = [
    # Digito verificador invalido.
    "CPF 123.456.789-08",
    "CNPJ 18.781.203/0001-29",
    "CNPJ 12.ABC.345/01DE-36",
    "PIS 120.54789.01-4",
    "cartao 700 0000 0000 0006",
    "titulo 1023 8501 0672",
    # Um digito a menos ou a mais.
    "CPF 123.456.789-0",
    "CPF 123.456.789-090",
    "telefone (11) 9123-5678",
    "telefone (11) 912345-5678",
    # Digitos todos iguais.
    "CPF 111.111.111-11",
    "CNPJ 00.000.000/0000-00",
    # Regra 2: valor em dinheiro e horario.
    "O total ficou em R$ 123.456.789,09.",
    "O total ficou em 12.345.678.909,00 no periodo.",
    "Entrega das 09:30-15:30.",
    "Cotacao 0,12345678909 hoje.",
    # Regra 3: colado em maiuscula ou em outro digito.
    "codigo AB12345678909",
    "codigo 12345678909X",
    # Regra 1: pedaco de sequencia maior nao e testado.
    "protocolo 9912345678909",
    "sequencia 12345678909 12054789013",
    # Celular: DDD que nao existe, e numero que nao comeca com 9.
    "telefone (20) 91234-5678",
    "telefone (11) 81234-5678",
    # Com +, o codigo do pais tem de ser 55 e o resto um celular completo.
    "telefone +54 11 91234-5678",
    "telefone +55 91 988-1234",
    # Endereco eletronico incompleto, perfil de rede social e nome de arquivo.
    "responda para fulano@",
    "responda para @example.com",
    "me segue no @fulano",
    "o anexo e logo@2x.png",
    "o anexo e foto@3x.jpg",
    # Numero comum.
    "Pedido 10001, nota 4521, protocolo 20261112.",
    "",
]


@pytest.mark.parametrize("texto", NAO_DETECTA)
def test_nao_detecta(texto: str) -> None:
    assert achar(texto) == []


# --- Regra 3 e separacao entre dados --------------------------------------------------


def test_colado_em_letra_minuscula_vale() -> None:
    # "nº" vira "no" na normalizacao (NFKC); a escrita sem espaco e comum.
    assert achar("CPF nº12345678909") == [("cpf", "12345678909")]


def test_dois_dados_separados_por_virgula_e_espaco() -> None:
    assert achar("12345678909, 12054789013") == [("cpf", "12345678909"), ("pis", "12054789013")]


def test_dois_dados_separados_por_texto() -> None:
    texto = "CPF 123.456.789-09 e e-mail fulano@example.com, celular (11) 91234-5678."
    assert achar(texto) == [
        ("cpf", "123.456.789-09"),
        ("email", "fulano@example.com"),
        ("telefone", "(11) 91234-5678"),
    ]


def test_quebra_de_linha_separa_dois_dados() -> None:
    assert achar("12345678909\n12054789013") == [("cpf", "12345678909"), ("pis", "12054789013")]


def test_cnpj_alfanumerico_depois_de_palavra_em_maiusculas() -> None:
    assert achar("CNPJ 12ABC34501DE35 ATIVO") == [("cnpj", "12ABC34501DE35")]
    assert achar("CNPJ 12 ABC 345 01DE 35") == [("cnpj", "12 ABC 345 01DE 35")]


def test_documento_dentro_de_endereco_eletronico_fica_coberto_pelo_endereco() -> None:
    # Uma deteccao contida em outra e descartada: fica a maior.
    assert achar("contato: joao12345678909@example.com") == [
        ("email", "joao12345678909@example.com")
    ]


# --- Regra 4: colisao em 11 digitos ---------------------------------------------------


def test_colisao_cpf_e_pis_rotula_cpf() -> None:
    numero = "29000000092"
    assert cpf_valido(numero) and pis_valido(numero) and not celular_valido(numero)
    assert achar(f"numero {numero}") == [("cpf", numero)]


def test_colisao_cpf_e_celular_rotula_cpf() -> None:
    numero = "11900000083"
    assert cpf_valido(numero) and celular_valido(numero) and not pis_valido(numero)
    assert achar(f"numero {numero}") == [("cpf", numero)]


def test_colisao_pis_e_celular_rotula_pis() -> None:
    numero = "11900000002"
    assert pis_valido(numero) and celular_valido(numero) and not cpf_valido(numero)
    assert achar(f"numero {numero}") == [("pis", numero)]


def test_com_parenteses_so_e_testado_como_celular() -> None:
    # Os mesmos digitos de 11900000083 (CPF e celular validos), escritos como telefone.
    assert achar("numero (11) 90000-0083") == [("telefone", "(11) 90000-0083")]


# --- Regra 5: posicao no texto original (RQ-07) ---------------------------------------


def test_largura_zero_entre_os_digitos_posicao_cobre_os_invisiveis() -> None:
    disfarcado = "​".join("12345678909")
    texto = f"meu CPF: {disfarcado}, obrigado"
    assert achar(texto) == [("cpf", disfarcado)]


def test_digitos_de_largura_total() -> None:
    disfarcado = "".join(chr(0xFF10 + int(d)) for d in "12345678909")
    assert achar(f"meu CPF: {disfarcado}.") == [("cpf", disfarcado)]


def test_um_espaco_entre_cada_digito() -> None:
    disfarcado = " ".join("12345678909")
    assert achar(f"meu CPF: {disfarcado}.") == [("cpf", disfarcado)]


def test_invisivel_antes_do_dado_desloca_a_posicao_corretamente() -> None:
    texto = "​​​meu CPF: 123.456.789-09"
    assert achar(texto) == [("cpf", "123.456.789-09")]


def test_ablacao_sem_normalizacao_o_disfarce_passa_e_o_resto_nao_muda() -> None:
    disfarcado = "​".join("12345678909")
    assert achar(f"meu CPF: {disfarcado}", normalizacao=False) == []
    # Sem disfarce, o resultado e o mesmo com o estagio ligado ou desligado.
    limpo = "meu CPF: 123.456.789-09 e fulano@example.com"
    assert achar(limpo, normalizacao=False) == achar(limpo, normalizacao=True)


# --- Forma do resultado ---------------------------------------------------------------


def test_deteccoes_em_ordem_sem_sobreposicao_e_marcadas_como_validas() -> None:
    texto = "fulano@example.com; 123.456.789-09; (11) 91234-5678; 1023 8501 0671"
    deteccoes = detectar_dados_pessoais(normalizar(texto))
    assert [d.tipo for d in deteccoes] == ["email", "cpf", "telefone", "titulo"]
    posicoes = [d.posicao for d in deteccoes]
    assert posicoes == sorted(posicoes)
    for (_, fim), (inicio, _) in zip(posicoes, posicoes[1:]):
        assert fim <= inicio
    assert all(d.valido for d in deteccoes)


def test_e_deterministica() -> None:
    texto = "CPF 123.456.789-09, PIS 120.54789.01-3"
    assert detectar_dados_pessoais(normalizar(texto)) == detectar_dados_pessoais(normalizar(texto))
