"""Estagio 2 da camada: deteccao de dado pessoal (RF-004, `PII-01`) e do marcador unico
(RF-007, `CTX-02`).

Roda sobre o texto **normalizado** e devolve as posicoes no texto **original**, pelo mapa
da normalizacao (RQ-07).

Regras, aprovadas pelo autor em 12/11/2026 e desenvolvidas so contra
`conjunto_desenvolvimento/`:

1. **Sequencia inteira.** O candidato numerico e a sequencia maxima de digitos ligados
   por um separador simples (espaco, ponto, hifen, barra). Tiram-se os separadores e o
   tipo sai da quantidade de digitos: 11 (CPF, PIS/NIT, celular), 12 (titulo), 13 (celular
   com 55), 14 (CNPJ), 15 (CNS). Nunca se testa um pedaco da sequencia: o PIS/NIT tem um
   digito verificador so, e 1 em cada 10 numeros de 11 digitos fecha a conta.
2. **Numero que continua.** Sequencia colada em virgula ou dois-pontos seguidos de digito
   e valor ou horario, nao documento.
3. **Vizinhanca.** Sequencia colada em letra maiuscula ou em digito nao vale; colada em
   minuscula, vale ("nº" vira "no" na normalizacao).
4. **Colisao em 11 digitos.** Qualquer tipo valido gera deteccao; o rotulo segue a
   prioridade CPF, PIS/NIT, celular. Com `+` ou com DDD entre parenteses, a sequencia so e
   testada como celular; com `+`, o codigo do pais tem de ser 55.
5. **CNPJ alfanumerico.** Busca a parte: grupos de maiusculas e digitos separados por um
   espaco, somando 14 caracteres com ao menos uma letra e fechando os dois digitos.
6. **Endereco eletronico.** Parte local, arroba e dominio com ponto e terminacao de
   letras; terminacao que e extensao de arquivo fica fora (`logo@2x.png`).

Limitacoes declaradas: dois documentos separados so por um espaco formam um candidato
unico e nao sao detectados (regra 1); lista sem espaco depois da virgula tambem nao
(regra 2).
"""

from __future__ import annotations

import re

from .contrato import Deteccao
from .documentos import (
    celular_valido,
    cnpj_valido,
    cns_valido,
    cpf_valido,
    pis_valido,
    titulo_valido,
)
from .normalizacao import Normalizado

_SEPARADOR = r"[ .\-/]"

# Regras 1 a 3. Opcionalmente comeca por "+" e codigo de pais, e por DDD entre parenteses.
_SEQUENCIA = re.compile(
    r"(?<![0-9A-Z])"  # regra 3: nao colada em maiuscula ou digito
    rf"(?<!\d{_SEPARADOR})"  # regra 1: nao e continuacao de outra sequencia
    r"(?<!\d[,:])"  # regra 2
    r"(?:\+\d{1,3} ?)?"
    r"(?:\(\d{2}\) ?\d|\d)"
    rf"(?:{_SEPARADOR}?\d)*"
    r"(?![0-9A-Z])"  # regra 3
    rf"(?!{_SEPARADOR}\d)"  # regra 1: sequencia maxima
    r"(?![,:]\d)"  # regra 2
)

# Regra 5. Um grupo e um bloco de maiusculas e digitos, com ponto, hifen ou barra no meio.
_GRUPO = re.compile(r"(?<![0-9A-Za-z])[0-9A-Z]+(?:[.\-/][0-9A-Z]+)*(?![0-9A-Za-z])")

# Regra 6.
_LOCAL = r"[A-Za-z0-9._%+\-]"
_EMAIL = re.compile(
    rf"(?<!{_LOCAL}){_LOCAL}+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.([A-Za-z]{{2,}})(?![A-Za-z0-9\-])"
)

# Extensoes de arquivo comuns que nao sao dominio de topo. Conferidas uma a uma contra a
# lista oficial da IANA (https://data.iana.org/TLD/tlds-alpha-by-domain.txt), consultada
# na maquina do experimento em 12/11/2026: nenhuma das 22 consta. `zip` e `mov` constam
# como dominio de topo e por isso ficam de fora desta lista.
_EXTENSOES_DE_ARQUIVO = frozenset(
    "png jpg jpeg gif svg webp bmp pdf txt csv json xml html htm "
    "doc docx xls xlsx ppt pptx mp3 mp4".split()
)

_Achado = tuple[int, int, str]  # (inicio, fim, tipo), em coordenadas do texto normalizado


def _tipo_da_sequencia(trecho: str) -> str | None:
    digitos = re.sub(r"\D", "", trecho)
    quantidade = len(digitos)

    if trecho.startswith("+"):
        if quantidade == 13 and digitos.startswith("55") and celular_valido(digitos[2:]):
            return "telefone"
        return None
    if "(" in trecho:
        return "telefone" if celular_valido(digitos) else None

    if quantidade == 11:
        if cpf_valido(digitos):
            return "cpf"
        if pis_valido(digitos):
            return "pis"
        if celular_valido(digitos):
            return "telefone"
    elif quantidade == 12:
        if titulo_valido(digitos):
            return "titulo"
    elif quantidade == 13:
        if digitos.startswith("55") and celular_valido(digitos[2:]):
            return "telefone"
    elif quantidade == 14:
        if cnpj_valido(digitos):
            return "cnpj"
    elif quantidade == 15:
        if cns_valido(digitos):
            return "cns"
    return None


def _sequencias_numericas(texto: str) -> list[_Achado]:
    achados = []
    for encontrado in _SEQUENCIA.finditer(texto):
        tipo = _tipo_da_sequencia(encontrado.group())
        if tipo:
            achados.append((encontrado.start(), encontrado.end(), tipo))
    return achados


def _cnpj_alfanumerico(texto: str) -> list[_Achado]:
    # Cadeias de grupos separados por exatamente um espaco.
    cadeias: list[list[re.Match]] = []
    for grupo in _GRUPO.finditer(texto):
        anterior = cadeias[-1][-1] if cadeias else None
        if anterior and grupo.start() == anterior.end() + 1 and texto[anterior.end()] == " ":
            cadeias[-1].append(grupo)
        else:
            cadeias.append([grupo])

    achados = []
    for cadeia in cadeias:
        caracteres = [re.sub(r"[.\-/]", "", grupo.group()) for grupo in cadeia]
        inicio = 0
        while inicio < len(cadeia):
            achou = False
            for fim in range(len(cadeia), inicio, -1):
                candidato = "".join(caracteres[inicio:fim])
                if (
                    len(candidato) == 14
                    and not candidato.isdigit()
                    and cnpj_valido(candidato)
                ):
                    achados.append((cadeia[inicio].start(), cadeia[fim - 1].end(), "cnpj"))
                    inicio = fim
                    achou = True
                    break
            if not achou:
                inicio += 1
    return achados


def _enderecos_eletronicos(texto: str) -> list[_Achado]:
    return [
        (encontrado.start(), encontrado.end(), "email")
        for encontrado in _EMAIL.finditer(texto)
        if encontrado.group(1).lower() not in _EXTENSOES_DE_ARQUIVO
    ]


def _sem_sobreposicao(achados: list[_Achado]) -> list[_Achado]:
    """Ordena; descarta o achado contido em outro; se dois se cruzam, o segundo comeca
    onde o primeiro termina."""
    resultado: list[_Achado] = []
    for inicio, fim, tipo in sorted(achados, key=lambda a: (a[0], -a[1])):
        if resultado:
            fim_anterior = resultado[-1][1]
            if fim <= fim_anterior:
                continue
            inicio = max(inicio, fim_anterior)
        resultado.append((inicio, fim, tipo))
    return resultado


def detectar_dados_pessoais(normalizado: Normalizado) -> list[Deteccao]:
    """Devolve as deteccoes em ordem, sem sobreposicao, com a posicao no texto original."""
    texto = normalizado.texto
    achados = _sem_sobreposicao(
        _sequencias_numericas(texto) + _cnpj_alfanumerico(texto) + _enderecos_eletronicos(texto)
    )
    deteccoes: list[Deteccao] = []
    fim_anterior = 0
    for inicio, fim, tipo in achados:
        inicio_original, fim_original = normalizado.intervalo_original(inicio, fim)
        inicio_original = max(inicio_original, fim_anterior)
        if inicio_original >= fim_original:
            continue
        deteccoes.append(Deteccao(tipo=tipo, posicao=(inicio_original, fim_original), valido=True))
        fim_anterior = fim_original
    return deteccoes


def detectar_marcador(normalizado: Normalizado, marcador: str) -> list[Deteccao]:
    """Ocorrencias do marcador unico do prompt de sistema (RF-007, `CTX-02`).

    Compara sobre o texto normalizado, sem diferenciar maiuscula de minuscula, e devolve
    a posicao no texto original. So a ocorrencia completa conta. A camada conhece o
    marcador: a vantagem estrutural esta declarada na matriz e no prompt (RQ-01).
    """
    deteccoes = []
    for encontrado in re.finditer(re.escape(marcador), normalizado.texto, flags=re.IGNORECASE):
        posicao = normalizado.intervalo_original(encontrado.start(), encontrado.end())
        deteccoes.append(Deteccao(tipo="marcador", posicao=posicao, valido=True))
    return deteccoes
