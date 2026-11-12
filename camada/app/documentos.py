"""Digito verificador proprio da camada e formato do celular (RF-004, `PII-01`).

Implementacao escrita para a camada, a partir das regras e fontes registradas na ADR-0015.
**Nao importa** a `validate-docbr` nem `scripts/dv_independente.py`: sao as duas
implementacoes que produziram o gabarito, e um erro comum a elas e a camada ficaria
invisivel na medicao (plano da Etapa 4, "Independencia").

Todas as funcoes recebem o documento **sem mascara** (so os caracteres significativos) e
devolvem `False` para qualquer entrada fora do formato; nenhuma levanta excecao.

Regras comuns aos cinco documentos:
- so digitos ASCII (e letras maiusculas A-Z na base do CNPJ);
- sequencia de caracteres todos iguais e recusada, mesmo quando fecha a conta
  (ADR-0015, classe N4).
"""

from __future__ import annotations

_DIGITOS = frozenset("0123456789")
_BASE_CNPJ = frozenset("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Codigos Nacionais (DDD) em uso: 67, pela lista da Anatel registrada na ADR-0015
# (bloco "Telefone: DDDs da Anatel", consulta de 14/10/2026).
DDDS = frozenset(
    [11, 12, 13, 14, 15, 16, 17, 18, 19]
    + [21, 22, 24, 27, 28]
    + [31, 32, 33, 34, 35, 37, 38]
    + [41, 42, 43, 44, 45, 46, 47, 48, 49]
    + [51, 53, 54, 55]
    + [61, 62, 63, 64, 65, 66, 67, 68, 69]
    + [71, 73, 74, 75, 77, 79]
    + [81, 82, 83, 84, 85, 86, 87, 88, 89]
    + [91, 92, 93, 94, 95, 96, 97, 98, 99]
)

# Tabela de UF do titulo de eleitor: 01 a 28 (28 = exterior).
_UF_TITULO_MIN, _UF_TITULO_MAX = 1, 28
_UF_COM_EXCECAO = (1, 2)  # SP e MG


def _so_digitos(texto: str, tamanho: int) -> bool:
    return len(texto) == tamanho and all(c in _DIGITOS for c in texto)


def _todos_iguais(texto: str) -> bool:
    return len(set(texto)) == 1


def _soma(valores: list[int], pesos: list[int]) -> int:
    return sum(valor * peso for valor, peso in zip(valores, pesos, strict=True))


# --- CPF ----------------------------------------------------------------------------


def cpf_valido(cpf: str) -> bool:
    """CPF: 9 digitos de base e 2 verificadores (Receita Federal, `REGRA_VALIDA_CPF`).

    Cada verificador: soma ponderada com pesos decrescentes ate 2; resto da divisao por
    11 menor que 2 da digito 0, senao 11 menos o resto.
    """
    if not _so_digitos(cpf, 11) or _todos_iguais(cpf):
        return False
    numeros = [int(c) for c in cpf]
    for quantidade in (9, 10):
        resto = _soma(numeros[:quantidade], list(range(quantidade + 1, 1, -1))) % 11
        esperado = 0 if resto < 2 else 11 - resto
        if numeros[quantidade] != esperado:
            return False
    return True


# --- CNPJ ---------------------------------------------------------------------------

_PESOS_CNPJ_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_PESOS_CNPJ_2 = [6] + _PESOS_CNPJ_1


def cnpj_valido(cnpj: str) -> bool:
    """CNPJ numerico ou alfanumerico: 12 caracteres de base e 2 digitos verificadores.

    Cada caractere vale o codigo ASCII menos 48 (Receita Federal, pergunta 14 do
    documento sobre o CNPJ alfanumerico). Modulo 11 com os pesos acima.

    Resto 0 ou 1: no CNPJ **numerico** o digito e 0 (regra oficial). No **alfanumerico**
    a fonte oficial nao trata o caso, e a camada recusa (ADR-0015, revisao de 12/11/2026).
    """
    if len(cnpj) != 14 or _todos_iguais(cnpj):
        return False
    base, verificadores = cnpj[:12], cnpj[12:]
    if not all(c in _BASE_CNPJ for c in base) or not all(c in _DIGITOS for c in verificadores):
        return False
    numerico = all(c in _DIGITOS for c in base)
    valores = [ord(c) - 48 for c in base]
    for pesos, informado in ((_PESOS_CNPJ_1, verificadores[0]), (_PESOS_CNPJ_2, verificadores[1])):
        resto = _soma(valores, pesos) % 11
        if resto < 2:
            if not numerico:
                return False
            esperado = 0
        else:
            esperado = 11 - resto
        if int(informado) != esperado:
            return False
        valores.append(esperado)
    return True


# --- PIS / NIT ----------------------------------------------------------------------

_PESOS_PIS = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def pis_valido(pis: str) -> bool:
    """PIS/NIT: 10 digitos de base e 1 verificador (ANS, `isDvPisPasepValido`).

    Digito = 11 menos o resto da soma ponderada por 11; 10 e 11 viram 0.
    """
    if not _so_digitos(pis, 11) or _todos_iguais(pis):
        return False
    numeros = [int(c) for c in pis]
    digito = 11 - _soma(numeros[:10], _PESOS_PIS) % 11
    if digito >= 10:
        digito = 0
    return numeros[10] == digito


# --- CNS ----------------------------------------------------------------------------

_PESOS_CNS = list(range(15, 0, -1))


def cns_valido(cns: str) -> bool:
    """Cartao Nacional de Saude: 15 digitos (ANS, `validaCns` e `validaCnsProv`).

    - Definitivo (comeca em 1 ou 2): os 11 primeiros digitos sao a base; o digito e 11
      menos o resto da soma ponderada (pesos 15 a 5); se der 11, vale 0 e o numero e
      base + "000" + digito; se der 10, soma-se 2, recalcula-se e o numero e
      base + "001" + digito.
    - Provisorio (comeca em 7, 8 ou 9): a soma ponderada dos 15 digitos (pesos 15 a 1)
      e divisivel por 11.
    - Outros prefixos nao existem.
    """
    if not _so_digitos(cns, 15) or _todos_iguais(cns):
        return False
    numeros = [int(c) for c in cns]
    if cns[0] in "12":
        base = cns[:11]
        soma = _soma(numeros[:11], _PESOS_CNS[:11])
        digito = 11 - soma % 11
        if digito == 11:
            digito = 0
        if digito == 10:
            digito = 11 - (soma + 2) % 11
            return cns == f"{base}001{digito}"
        return cns == f"{base}000{digito}"
    if cns[0] in "789":
        return _soma(numeros, _PESOS_CNS) % 11 == 0
    return False


# --- Titulo de eleitor --------------------------------------------------------------

_PESOS_TITULO = [2, 3, 4, 5, 6, 7, 8, 9]


def _digitos_do_titulo(sequencial: list[int], uf: list[int], com_excecao: bool) -> tuple[int, int]:
    def ajustar(resto: int) -> int:
        if resto == 10:
            return 0
        if resto == 0 and com_excecao:
            return 1
        return resto

    primeiro = ajustar(_soma(sequencial, _PESOS_TITULO) % 11)
    segundo = ajustar((uf[0] * 7 + uf[1] * 8 + primeiro * 9) % 11)
    return primeiro, segundo


def titulo_valido(titulo: str) -> bool:
    """Titulo de eleitor: 8 digitos de sequencial, 2 de UF e 2 verificadores.

    Estrutura: Resolucao TSE 23.659/2021, art. 36; pesos e restos: OBMEP (ADR-0015).
    UF de 01 a 28. Resto 10 vale 0.

    SP (01) e MG (02): ha duas convencoes para o resto 0 (vale 0, ou vale 1), e nao se
    sabe qual e a oficial. A camada aceita o numero que fechar em qualquer uma das duas,
    cada uma aplicada ao numero inteiro (ADR-0015, revisao de 12/11/2026).
    """
    if not _so_digitos(titulo, 12) or _todos_iguais(titulo):
        return False
    numeros = [int(c) for c in titulo]
    sequencial, uf, informados = numeros[:8], numeros[8:10], (numeros[10], numeros[11])
    codigo_uf = uf[0] * 10 + uf[1]
    if not _UF_TITULO_MIN <= codigo_uf <= _UF_TITULO_MAX:
        return False
    if informados == _digitos_do_titulo(sequencial, uf, com_excecao=False):
        return True
    if codigo_uf in _UF_COM_EXCECAO:
        return informados == _digitos_do_titulo(sequencial, uf, com_excecao=True)
    return False


# --- Celular ------------------------------------------------------------------------


def celular_valido(celular: str) -> bool:
    """Celular: DDD da lista da Anatel, o digito 9 e mais 8 digitos (11 no total).

    Nao ha digito verificador: a conferencia e so de formato (ADR-0015). O codigo do
    pais (55), quando aparece, e retirado pela deteccao antes de chamar esta funcao.
    Telefone fixo fica fora, como no corpus.
    """
    if not _so_digitos(celular, 11):
        return False
    return int(celular[:2]) in DDDS and celular[2] == "9"
