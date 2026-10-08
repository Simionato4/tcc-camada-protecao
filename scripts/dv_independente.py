"""Implementacao independente dos digitos verificadores (ADR-0015, opcao A').

POR QUE EXISTE. A camada valida documentos com a `validate-docbr`. Se o corpus de PII
fosse gerado e conferido pela mesma biblioteca, um erro dela entraria no gabarito e no
detector ao mesmo tempo, e a camada pareceria acertar onde o gabarito esta errado. Este
modulo nao importa a `validate-docbr`: cada positivo do corpus precisa passar aqui E la.

Cada funcao cita a fonte de que foi escrita e o nivel dessa fonte. As fontes estao
registradas na ADR-0015 (revisao de 08/10/2026, segundo bloco).

Convencao: `completar_*` recebe a base e devolve o numero completo, so digitos (ou
digitos e letras, no CNPJ alfanumerico), ou None quando a fonte nao define o resultado.
"""

from __future__ import annotations


def _soma(valores: list[int], pesos: list[int]) -> int:
    return sum(v * p for v, p in zip(valores, pesos))


def _digitos(texto: str) -> list[int]:
    if not texto.isdigit():
        raise ValueError("esperados apenas digitos")
    return [int(c) for c in texto]


# --------------------------------------------------------------------------- CPF
# Fonte: Receita Federal, Manual de Preenchimento da e-Financeira, Anexo II,
# REGRA_VALIDA_CPF. Nivel: regra oficial. DV = resto da divisao por 11 da soma ponderada
# por 1..9 (primeiro) e 0..9 (segundo, incluindo o primeiro DV); resto 10 vale 0.

def completar_cpf(base9: str) -> str:
    d = _digitos(base9)
    if len(d) != 9:
        raise ValueError("CPF: base de 9 digitos")
    dv1 = _soma(d, list(range(1, 10))) % 11 % 10
    dv2 = _soma(d + [dv1], list(range(0, 10))) % 11 % 10
    return base9 + f"{dv1}{dv2}"


# -------------------------------------------------------------------------- CNPJ
# Fontes: (a) numerico: e-Financeira, Anexo II, REGRA_VALIDA_CNPJ (regra oficial):
# pesos 6,7,8,9,2,3,4,5,6,7,8,9 e 5,6,7,8,9,2,...,9; DV = resto; resto 10 vale 0.
# (b) alfanumerico: Receita Federal, perguntas e respostas sobre o CNPJ alfanumerico,
# pergunta 14 (regra oficial): valor = ASCII - 48; pesos 5..2 e 6..2; DV = 11 - resto.
# A pergunta 14 nao define resto 0 ou 1; para base com letra, devolve None nesse caso.

_CNPJ_P1 = [6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9]
_CNPJ_P2 = [5] + _CNPJ_P1
_ALFA_P1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_ALFA_P2 = [6] + _ALFA_P1


def completar_cnpj(base12: str) -> str | None:
    if len(base12) != 12:
        raise ValueError("CNPJ: base de 12 caracteres")
    if base12.isdigit():
        d = _digitos(base12)
        dv1 = _soma(d, _CNPJ_P1) % 11 % 10
        dv2 = _soma(d + [dv1], _CNPJ_P2) % 11 % 10
        return base12 + f"{dv1}{dv2}"
    if not all(c.isdigit() or ("A" <= c <= "Z") for c in base12):
        raise ValueError("CNPJ alfanumerico: digitos e letras maiusculas A-Z")
    valores = [ord(c) - 48 for c in base12]
    r1 = _soma(valores, _ALFA_P1) % 11
    if r1 < 2:
        return None
    dv1 = 11 - r1
    r2 = _soma(valores + [dv1], _ALFA_P2) % 11
    if r2 < 2:
        return None
    return base12 + f"{dv1}{11 - r2}"


# ---------------------------------------------------------------------- PIS/NIT
# Fonte: ANS, "Algoritmos do Aplicativo de Carga", item 7 (isDvPisPasepValido).
# Nivel: documentacao tecnica oficial (a ANS nao e o orgao emissor). Pesos
# 3,2,9,8,7,6,5,4,3,2; DV = 11 - resto; resultado 10 ou 11 vale 0.

def completar_pis(base10: str) -> str:
    d = _digitos(base10)
    if len(d) != 10:
        raise ValueError("PIS/NIT: base de 10 digitos")
    dv = 11 - _soma(d, [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]) % 11
    return base10 + str(0 if dv >= 10 else dv)


# --------------------------------------------------------------------------- CNS
# Fonte: ANS, "Algoritmos do Aplicativo de Carga", item 4 (validaCns, validaCnsProv).
# Nivel: documentacao tecnica oficial. Separacao por prefixo (1 e 2 definitivo; 7, 8 e
# 9 provisorio): documentacao de integracao do e-SUS APS, v2.1.1.

_PESOS_15 = list(range(15, 0, -1))


def completar_cns_definitivo(base11: str) -> str:
    d = _digitos(base11)
    if len(d) != 11 or d[0] not in (1, 2):
        raise ValueError("CNS definitivo: base de 11 digitos iniciada por 1 ou 2")
    soma = _soma(d, _PESOS_15[:11])
    dv = 11 - soma % 11
    if dv == 11:
        dv = 0
    if dv == 10:
        soma += 2
        dv = 11 - soma % 11
        return base11 + "001" + str(dv)
    return base11 + "000" + str(dv)


def completar_cns_provisorio(base14: str) -> str | None:
    """Ultimo digito que torna a soma ponderada por 15..1 multipla de 11; None se
    esse digito seria 10."""
    d = _digitos(base14)
    if len(d) != 14 or d[0] not in (7, 8, 9):
        raise ValueError("CNS provisorio: base de 14 digitos iniciada por 7, 8 ou 9")
    ultimo = (-_soma(d, _PESOS_15[:14])) % 11
    return None if ultimo == 10 else base14 + str(ultimo)


def cns_valido(numero: str) -> bool:
    if len(numero) != 15 or not numero.isdigit() or numero == "0" * 15:
        return False
    d = _digitos(numero)
    if d[0] in (1, 2):
        return completar_cns_definitivo(numero[:11]) == numero
    if d[0] in (7, 8, 9):
        return _soma(d, _PESOS_15) % 11 == 0
    return False


# ------------------------------------------------------------------------ Titulo
# Estrutura: Resolucao TSE 23.659/2021, art. 36, paragrafo unico (oficial): 8 algarismos
# sequenciais, 2 da UF (01 a 28), 2 verificadores por modulo 11, o primeiro sobre o
# sequencial e o segundo sobre a UF seguida do primeiro DV.
# Pesos e tratamento do resto: OBMEP, "A Matematica nos Documentos: Titulo de Eleitor".
# Nivel: fonte academica secundaria; NAO e regra oficial. Pesos 2..9 e 7,8,9; DV = resto;
# resto 10 vale 0; em SP (01) e MG (02), resto 0 vale 1.

def completar_titulo(sequencial8: str, uf: str, excecao_sp_mg: bool = True) -> str:
    """`excecao_sp_mg=False` reproduz a convencao da validate-docbr 2.0.0, que nao aplica
    a excecao (divergencia registrada na ADR-0015)."""
    s = _digitos(sequencial8)
    u = _digitos(uf)
    if len(s) != 8 or len(u) != 2 or not 1 <= int(uf) <= 28:
        raise ValueError("Titulo: sequencial de 8 digitos e UF de 01 a 28")

    def dv(resto: int) -> int:
        if resto == 10:
            return 0
        if resto == 0 and excecao_sp_mg and uf in ("01", "02"):
            return 1
        return resto

    dv1 = dv(_soma(s, [2, 3, 4, 5, 6, 7, 8, 9]) % 11)
    dv2 = dv(_soma(u + [dv1], [7, 8, 9]) % 11)
    return sequencial8 + uf + f"{dv1}{dv2}"


def titulo_ambiguo(sequencial8: str, uf: str) -> bool:
    """True quando as duas convencoes (com e sem a excecao de SP e MG) dao DV diferentes.
    Esses numeros nao tem gabarito inequivoco e ficam fora dos positivos do corpus."""
    return completar_titulo(sequencial8, uf, True) != completar_titulo(sequencial8, uf, False)
