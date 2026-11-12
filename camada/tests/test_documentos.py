"""Digito verificador proprio da camada (Etapa 4, T013; RF-004, `PII-01`).

Os valores abaixo sao de dois tipos, e nenhum vem do corpus congelado, do conjunto de
desenvolvimento ou de `scripts/dv_independente.py`:
- **exemplos publicados** nas fontes citadas na ADR-0015 (Receita Federal e OBMEP);
- **valores calculados a mao** para este arquivo, com a conta no comentario, escolhidos
  para cair nos casos de borda de cada regra (resto 0, 1 e 10).

As funcoes recebem o documento **sem mascara**: so os caracteres significativos. Tirar
pontos, tracos e barras e trabalho da deteccao (T016).
"""

import pytest

from camada.app.documentos import (
    cnpj_valido,
    cns_valido,
    cpf_valido,
    pis_valido,
    titulo_valido,
)

# --- CPF: pesos 10..2 e 11..2; resto < 2 da digito 0, senao 11 - resto ---------------

CPF_VALIDOS = [
    # Exemplo da Receita Federal (e-Financeira, REGRA_VALIDA_CPF), citado na ADR-0015.
    # 1a soma 162, resto 8, digito 3; 2a soma 201, resto 3, digito 8.
    "28001238938",
    # Base 123456789. 1a soma: 10+18+24+28+30+30+28+24+18 = 210, resto 1 -> digito 0.
    # 2a soma: 11+20+27+32+35+36+35+32+27+0 = 255, resto 2 -> digito 9.
    "12345678909",
    # Base 100000000. 1a soma 10, resto 10 -> digito 1. 2a soma 11+2 = 13, resto 2 -> 9.
    "10000000019",
]


@pytest.mark.parametrize("cpf", CPF_VALIDOS)
def test_cpf_valido(cpf: str) -> None:
    assert cpf_valido(cpf)


@pytest.mark.parametrize("cpf", CPF_VALIDOS)
def test_cpf_com_ultimo_digito_trocado_e_recusado(cpf: str) -> None:
    trocado = cpf[:-1] + str((int(cpf[-1]) + 1) % 10)
    assert not cpf_valido(trocado)


def test_cpf_com_primeiro_digito_verificador_trocado_e_recusado() -> None:
    assert not cpf_valido("12345678919")


# --- CNPJ: pesos 5,4,3,2,9..2 e 6,5,4,3,2,9..2; caractere vale ASCII - 48 ------------

CNPJ_VALIDOS = [
    # Exemplo numerico da Receita Federal (e-Financeira, REGRA_VALIDA_CNPJ).
    # 1a soma 119, resto 9, digito 2; 2a soma 146, resto 3, digito 8.
    "18781203000128",
    # Exemplo alfanumerico da Receita Federal (perguntas e respostas, pergunta 14).
    # Valores: 1,2,17,18,19,3,4,5,0,1,20,21. 1a soma 459, resto 8, digito 3;
    # 2a soma 424, resto 6, digito 5.
    "12ABC34501DE35",
    # Numerico, base 000000000019. 1a soma 3 + 18 = 21, resto 10 -> digito 1.
    # 2a soma 4 + 27 + 2 = 33, resto 0 -> digito 0 (regra oficial do CNPJ numerico).
    "00000000001910",
]


@pytest.mark.parametrize("cnpj", CNPJ_VALIDOS)
def test_cnpj_valido(cnpj: str) -> None:
    assert cnpj_valido(cnpj)


@pytest.mark.parametrize("cnpj", CNPJ_VALIDOS)
def test_cnpj_com_ultimo_digito_trocado_e_recusado(cnpj: str) -> None:
    trocado = cnpj[:-1] + str((int(cnpj[-1]) + 1) % 10)
    assert not cnpj_valido(trocado)


@pytest.mark.parametrize("dv", [f"{n:02d}" for n in range(100)])
def test_cnpj_alfanumerico_com_resto_0_ou_1_e_recusado(dv: str) -> None:
    # Base A00000000007: A vale 17. 1a soma 17*5 + 7*2 = 99, resto 0. A regra oficial do
    # alfanumerico nao diz o que fazer com resto 0 ou 1 (ADR-0015): a camada recusa,
    # qualquer que seja o par de digitos.
    assert not cnpj_valido("A00000000007" + dv)


def test_cnpj_com_letra_minuscula_e_recusado() -> None:
    assert not cnpj_valido("12abc34501de35")


def test_cnpj_com_letra_no_digito_verificador_e_recusado() -> None:
    assert not cnpj_valido("12ABC34501DE3A")


# --- PIS/NIT: pesos 3,2,9,8,7,6,5,4,3,2; digito 11 - resto; 10 e 11 viram 0 ----------

PIS_VALIDOS = [
    # Base 1205478901: 3+4+0+40+28+42+40+36+0+2 = 195, resto 8 -> digito 3.
    "12054789013",
    # Base 1234567890: 3+4+27+32+35+36+35+32+27+0 = 231, resto 0 -> 11 -> digito 0.
    "12345678900",
    # Base 1000000030: 3 + 9 = 12, resto 1 -> 10 -> digito 0.
    "10000000300",
    # Base 1000000000: soma 3, resto 3 -> digito 8.
    "10000000008",
]


@pytest.mark.parametrize("pis", PIS_VALIDOS)
def test_pis_valido(pis: str) -> None:
    assert pis_valido(pis)


@pytest.mark.parametrize("pis", PIS_VALIDOS)
def test_pis_com_ultimo_digito_trocado_e_recusado(pis: str) -> None:
    trocado = pis[:-1] + str((int(pis[-1]) + 1) % 10)
    assert not pis_valido(trocado)


# --- CNS: pesos 15..1 --------------------------------------------------------------

CNS_VALIDOS = [
    # Definitivo (comeca em 1 ou 2), regra `validaCns` da ANS. Base 10000000000:
    # soma 1*15 = 15, resto 4, digito 7 -> base + "000" + "7".
    "100000000000007",
    # Definitivo, caso em que o digito daria 10. Base 25000000000: soma 30 + 70 = 100,
    # resto 1 -> digito 10 -> soma + 2 = 102, resto 3, digito 8 -> base + "001" + "8".
    "250000000000018",
    # Provisorio (comeca em 7, 8 ou 9), regra `validaCnsProv`: soma ponderada divisivel
    # por 11. 7*15 + 5*1 = 110.
    "700000000000005",
    # 8*15 + 1*1 = 121.
    "800000000000001",
    # 9*15 + 8*1 = 143.
    "900000000000008",
]


@pytest.mark.parametrize("cns", CNS_VALIDOS)
def test_cns_valido(cns: str) -> None:
    assert cns_valido(cns)


@pytest.mark.parametrize("cns", CNS_VALIDOS)
def test_cns_com_ultimo_digito_trocado_e_recusado(cns: str) -> None:
    trocado = cns[:-1] + str((int(cns[-1]) + 1) % 10)
    assert not cns_valido(trocado)


def test_cns_definitivo_com_complemento_fora_da_regra_e_recusado() -> None:
    # Soma ponderada 15 + 4 + 3 = 22, divisivel por 11, mas o complemento depois da base
    # nao e "000" nem "001": pela regra da ANS para o definitivo, nao e valido.
    assert not cns_valido("100000000001003")


@pytest.mark.parametrize("prefixo", ["0", "3", "4", "5", "6"])
def test_cns_com_prefixo_inexistente_e_recusado(prefixo: str) -> None:
    # Completa com o digito que fecha a soma, para o motivo da recusa ser so o prefixo.
    soma = int(prefixo) * 15
    ultimo = (11 - soma % 11) % 11
    if ultimo < 10:
        assert not cns_valido(prefixo + "0" * 13 + str(ultimo))


# --- Titulo de eleitor: 8 de sequencial + 2 de UF + 2 digitos -----------------------
# 1o digito: sequencial com pesos 2..9, resto da divisao por 11; resto 10 vale 0.
# 2o digito: UF com pesos 7 e 8, mais o 1o digito com peso 9; resto 10 vale 0.

TITULOS_VALIDOS = [
    # Exemplo da OBMEP, citado na ADR-0015. 2+0+8+15+48+35+0+9 = 117, resto 7.
    # 0*7 + 6*8 + 7*9 = 111, resto 1.
    "102385010671",
    # UF 28 (exterior), limite superior da tabela. Mesmo sequencial, 1o digito 7.
    # 2*7 + 8*8 + 7*9 = 141, resto 9.
    "102385012879",
    # Resto 10 no 1o digito. Sequencial 50000000: soma 10 -> digito 0.
    # UF 06: 48 + 0 = 48, resto 4.
    "500000000604",
    # Fora de SP e MG, resto 0 vale 0. Sequencial 10000001: 2 + 9 = 11, resto 0.
    # UF 06: 48 + 0 = 48, resto 4.
    "100000010604",
]

# SP (01) e MG (02): vale o numero que fechar em qualquer uma das duas convencoes
# (ADR-0015, revisao de 12/11/2026). Pares (sem excecao, com excecao).
TITULOS_SP_MG = [
    # 1o digito com resto 0. Sequencial 10000001, UF 01.
    # Sem excecao: digito 0; 0 + 8 + 0 = 8.  Com excecao: digito 1; 8 + 9 = 17, resto 6.
    ("100000010108", "100000010116"),
    # 2o digito com resto 0. Sequencial 20000000 (soma 4, digito 4), UF 01.
    # 0 + 8 + 36 = 44, resto 0. Sem excecao: 0.  Com excecao: 1.
    ("200000000140", "200000000141"),
    # 2o digito com resto 0 em MG. Sequencial 40000000 (soma 8, digito 8), UF 02.
    # 0 + 16 + 72 = 88, resto 0. Sem excecao: 0.  Com excecao: 1.
    ("400000000280", "400000000281"),
]


@pytest.mark.parametrize("titulo", TITULOS_VALIDOS)
def test_titulo_valido(titulo: str) -> None:
    assert titulo_valido(titulo)


@pytest.mark.parametrize("titulo", TITULOS_VALIDOS)
def test_titulo_com_ultimo_digito_trocado_e_recusado(titulo: str) -> None:
    # Soma 5 para nao cair, por acaso, na outra convencao de SP e MG.
    trocado = titulo[:-1] + str((int(titulo[-1]) + 5) % 10)
    assert not titulo_valido(trocado)


@pytest.mark.parametrize("sem_excecao,com_excecao", TITULOS_SP_MG)
def test_titulo_de_sp_e_mg_vale_nas_duas_convencoes(sem_excecao: str, com_excecao: str) -> None:
    assert titulo_valido(sem_excecao)
    assert titulo_valido(com_excecao)


def test_excecao_de_sp_e_mg_nao_vale_em_outra_uf() -> None:
    # Sequencial 10000001 (resto 0) com UF 06. Com o digito 1 da excecao, o 2o digito
    # seria 48 + 9 = 57, resto 2. Fora de SP e MG, esse numero nao vale.
    assert not titulo_valido("100000010612")


def test_titulo_de_sp_nao_mistura_as_duas_convencoes() -> None:
    # Sequencial 10000001, UF 01: 1o digito da excecao (1) com o 2o digito calculado
    # sem ela (8), e o contrario. Nenhuma das duas convencoes produz esses numeros.
    assert not titulo_valido("100000010118")
    assert not titulo_valido("100000010106")


@pytest.mark.parametrize("uf", ["00", "29", "99"])
def test_titulo_com_uf_inexistente_e_recusado(uf: str) -> None:
    # Digitos calculados para a UF dada, para o motivo da recusa ser so a UF.
    primeiro = 7  # sequencial 10238501
    segundo = (int(uf[0]) * 7 + int(uf[1]) * 8 + primeiro * 9) % 11 % 10
    assert not titulo_valido("10238501" + uf + str(primeiro) + str(segundo))


# --- Regras comuns ------------------------------------------------------------------

VALIDADORES = [
    (cpf_valido, 11, "12345678909"),
    (cnpj_valido, 14, "18781203000128"),
    (pis_valido, 11, "12054789013"),
    (cns_valido, 15, "700000000000005"),
    (titulo_valido, 12, "102385010671"),
]
IDS = ["cpf", "cnpj", "pis", "cns", "titulo"]


@pytest.mark.parametrize("validador,tamanho,_", VALIDADORES, ids=IDS)
@pytest.mark.parametrize("digito", "0123456789")
def test_digitos_todos_iguais_sao_recusados(validador, tamanho: int, _: str, digito: str) -> None:
    # Parte dessas sequencias fecha a conta (o CPF de onze algarismos 1, por exemplo).
    # A recusa e regra a parte (ADR-0015, classe N4).
    assert not validador(digito * tamanho)


@pytest.mark.parametrize("validador,tamanho,valido", VALIDADORES, ids=IDS)
def test_comprimento_errado_e_recusado(validador, tamanho: int, valido: str) -> None:
    assert not validador(valido[:-1])
    assert not validador(valido + "0")
    assert not validador("")


@pytest.mark.parametrize("validador,tamanho,valido", VALIDADORES, ids=IDS)
def test_caractere_que_nao_e_do_documento_e_recusado(validador, tamanho: int, valido: str) -> None:
    assert not validador(valido[:3] + "." + valido[4:])
    assert not validador(valido[:3] + " " + valido[4:])
    assert not validador(valido[:3] + "１" + valido[4:])  # digito de largura total
