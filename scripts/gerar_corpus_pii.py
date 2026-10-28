"""Tarefa 3.6 - gera o corpus de documentos brasileiros (ADR-0015).

350 positivos e 350 negativos dificeis, em frases de atendimento com 1 a 3 ocorrencias
cada, com gabarito por posicao no texto ORIGINAL (RQ-07). Semente fixa.

Garantias, conferidas aqui mesmo antes de gravar:
- todo positivo e valido no proprio tipo pela `validate-docbr` E por
  `scripts/dv_independente.py`, e nao e valido em nenhum outro tipo do mesmo comprimento;
- todo negativo e invalido em todos os tipos do seu comprimento, nas duas implementacoes;
- numero "indefinido" (titulo ambiguo de SP e MG, CNPJ alfanumerico sem regra para o
  resto) nao entra;
- o telefone participa da regra de colisao: celular sem mascara tem 11 digitos, como CPF
  e PIS/NIT;
- endereco eletronico so em dominio reservado (RFC 2606 e 6761);
- `texto[inicio:fim] == valor` para toda ocorrencia;
- formato de mascara dos positivos de documento em tres partes - completa, ausente e
  parcial - e o telefone em cinco formatos, o quinto parcial; metade da N1 em formato
  parcial, para que a formatacao parcial nao seja pista exclusiva de positivo
  (revisao de 28/10/2026 da ADR-0015).

As frases-modelo foram escritas com assistencia de IA (o corpus e sintetico por desenho);
nao confundir com as mensagens legitimas da tarefa 3.8, de autoria do autor.

Uso:
    python scripts/gerar_corpus_pii.py --amostra 8   # imprime 8 textos; nao grava nada
    python scripts/gerar_corpus_pii.py               # grava e imprime o sha256

NENHUM DADO PESSOAL REAL: numeros sorteados, nunca associados a nome ou atributo.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import os
import random
import string
import sys
from pathlib import Path

from validate_docbr import CNPJ, CNS, CPF, PIS, TituloEleitoral

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "conjunto_teste" / "pii" / "corpus.jsonl"

_spec = importlib.util.spec_from_file_location("dv_independente", RAIZ / "scripts" / "dv_independente.py")
dv = importlib.util.module_from_spec(_spec)
sys.modules["dv_independente"] = dv
_spec.loader.exec_module(dv)

# 67 Codigos Nacionais, Anatel, FAQ "Areas Tarifarias", pergunta 6 (ADR-0015).
DDDS = (
    "11 12 13 14 15 16 17 18 19 21 22 24 27 28 31 32 33 34 35 37 38 41 42 43 44 45 46 47 "
    "48 49 51 53 54 55 61 62 63 64 65 66 67 68 69 71 73 74 75 77 79 81 82 83 84 85 86 87 "
    "88 89 91 92 93 94 95 96 97 98 99"
).split()
DOMINIOS = ("example.com", "example.net", "example.org")  # RFC 2606 e 6761

DOCUMENTOS = ("cpf", "cnpj", "cns", "pis", "titulo")
TIPOS = DOCUMENTOS + ("telefone", "email")
NATUREZA = {t: "pessoa_natural" for t in TIPOS} | {"cnpj": "pessoa_juridica"}
BIBLIOTECA = {"cpf": CPF, "cnpj": CNPJ, "cns": CNS, "pis": PIS, "titulo": TituloEleitoral}

POSITIVOS_POR_TIPO = 50
# Formato da mascara dos positivos de documento (revisao de 28/10/2026, ADR-0015):
# i % 3 sobre os 50 positivos da 17 completa, 17 ausente e 16 parcial.
FORMATOS_MASCARA = ("completa", "ausente", "parcial")
CONTAGEM_FORMATOS = {"completa": 17, "ausente": 17, "parcial": 16}
FORMATOS_TELEFONE = 5  # 0 a 3 como antes; 4 = parcial
N1_PARCIAIS = 5  # dos 10 negativos N1 de cada documento
CLASSES_DOC = ("N1", "N2", "N3", "N4", "N5")
CLASSES = {d: CLASSES_DOC for d in DOCUMENTOS} | {"telefone": ("T1", "T2"), "email": ("E1", "E2")}
POR_CLASSE = {d: 10 for d in DOCUMENTOS} | {"telefone": 25, "email": 25}
# Excecao declarada (ADR-0015): no CPF e no PIS/NIT, onze algarismos 9 tambem e celular
# valido pela regra de formato (DDD 99, 9, mais oito digitos) e nao pode ser negativo.
# No titulo, doze zeros e aceito pela biblioteca (UF 00; terceiro achado da ADR-0015) e,
# pela regra de colisao, numero que so a biblioteca aceita nao entra.
# Nesses tres tipos a N4 fica com 9 casos, e o caso que falta vai para a N2.
EXCECOES = {
    ("cpf", "N4"): 9, ("cpf", "N2"): 11,
    ("pis", "N4"): 9, ("pis", "N2"): 11,
    ("titulo", "N4"): 9, ("titulo", "N2"): 11,
}


def esperado(tipo: str, classe: str) -> int:
    return EXCECOES.get((tipo, classe), POR_CLASSE[tipo])


# ------------------------------------------------------------------ regra de colisao

def _so_caracteres(valor: str) -> str:
    return "".join(c for c in valor if c.isalnum()).upper()


def telefone_valido(nucleo: str) -> bool:
    """Celular brasileiro sem mascara: DDD da lista, 9, mais 8 digitos (ADR-0015)."""
    if nucleo.startswith("55") and len(nucleo) == 13:
        nucleo = nucleo[2:]
    return len(nucleo) == 11 and nucleo.isdigit() and nucleo[:2] in DDDS and nucleo[2] == "9"


def estados(nucleo: str) -> dict[str, tuple[str, bool]]:
    """Para cada tipo do mesmo comprimento: (estado independente, aceito pela biblioteca)."""
    saida: dict[str, tuple[str, bool]] = {}
    for tipo in DOCUMENTOS:
        if len(nucleo) == dv.COMPRIMENTO[tipo] and (nucleo.isdigit() or tipo == "cnpj"):
            saida[tipo] = (dv.estado(tipo, nucleo), BIBLIOTECA[tipo]().validate(nucleo))
    if nucleo.isdigit() and len(nucleo) in (11, 13):
        v = telefone_valido(nucleo)
        saida["telefone"] = (dv.VALIDO if v else dv.INVALIDO, v)
    return saida


def positivo_aceitavel(tipo: str, nucleo: str) -> bool:
    e = estados(nucleo)
    if e.get(tipo) != (dv.VALIDO, True):
        return False
    return all(par == (dv.INVALIDO, False) for t, par in e.items() if t != tipo)


def negativo_aceitavel(nucleo: str) -> bool:
    return all(par == (dv.INVALIDO, False) for par in estados(nucleo).values())


def valor_negativo_aceitavel(valor: str) -> bool:
    """Confere o valor COMO APARECE NO TEXTO: a formatacao pode criar outra sequencia de
    digitos (por exemplo, o prefixo +55 de um telefone curto vira um numero de 11
    digitos que fecha a conta do CPF)."""
    return negativo_aceitavel(_so_caracteres(valor))


# ------------------------------------------------------------------------ mascaras

def mascarar(tipo: str, n: str) -> str:
    if tipo == "cpf":
        return f"{n[:3]}.{n[3:6]}.{n[6:9]}-{n[9:]}"
    if tipo == "pis":
        return f"{n[:3]}.{n[3:8]}.{n[8:10]}-{n[10:]}"
    if tipo == "cnpj":
        return f"{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:]}"
    if tipo == "cns":
        return f"{n[:3]} {n[3:7]} {n[7:11]} {n[11:]}"
    if tipo == "titulo":
        return f"{n[:4]} {n[4:8]} {n[8:]}"
    raise ValueError(tipo)


def mascarar_parcial(r: random.Random, tipo: str, n: str) -> str:
    """Mascara parcial (revisao de 28/10/2026, ADR-0015), regra unica para os cinco
    documentos: a mascara oficial com pelo menos um separador removido e pelo menos um
    mantido; ou, quando a mascara nao e so de espacos, todos os separadores trocados por
    espaco. O resultado nunca e igual a mascara completa nem ao numero sem mascara."""
    completa = mascarar(tipo, n)
    separadores = [i for i, c in enumerate(completa) if not c.isalnum()]
    so_espacos = all(completa[i] == " " for i in separadores)
    if not so_espacos and r.random() < 0.5:
        return "".join(" " if i in separadores else c for i, c in enumerate(completa))
    remover = set(r.sample(separadores, r.randint(1, len(separadores) - 1)))
    return "".join(c for i, c in enumerate(completa) if i not in remover)


def formatar_telefone(n: str, estilo: int, r: random.Random | None = None) -> str:
    """Estilos 0 a 3 como na versao de 14/10; o 4 e parcial (revisao de 28/10/2026): o
    estilo 0 sem o espaco, sem o hifen ou sem os parenteses, sorteado."""
    ddd, resto = n[:2], n[2:]
    meio = len(resto) - 4
    estilo %= FORMATOS_TELEFONE
    if estilo == 4:
        return r.choice((
            f"({ddd}){resto[:meio]}-{resto[meio:]}",
            f"({ddd}) {resto}",
            f"{ddd} {resto[:meio]}-{resto[meio:]}",
        ))
    return (
        f"({ddd}) {resto[:meio]}-{resto[meio:]}",
        f"{ddd}{resto}",
        f"+55 {ddd} {resto[:meio]}-{resto[meio:]}",
        f"{ddd} {resto[:meio]} {resto[meio:]}",
    )[estilo]


# ------------------------------------------------------------- geradores de nucleo

def _digitos(r: random.Random, n: int) -> str:
    return "".join(r.choice(string.digits) for _ in range(n))


def nucleo_positivo(r: random.Random, tipo: str, alfanumerico: bool = False) -> str:
    while True:
        if tipo == "cpf":
            n = dv.completar_cpf(_digitos(r, 9))
        elif tipo == "pis":
            n = dv.completar_pis(_digitos(r, 10))
        elif tipo == "cnpj":
            alfabeto = string.digits + string.ascii_uppercase if alfanumerico else string.digits
            base = "".join(r.choice(alfabeto) for _ in range(12))
            if alfanumerico and base.isdigit():
                continue
            n = dv.completar_cnpj(base)
            if n is None:
                continue
        elif tipo == "cns":
            if r.random() < 0.5:
                n = dv.completar_cns_definitivo(r.choice("12") + _digitos(r, 10))
            else:
                n = dv.completar_cns_provisorio(r.choice("789") + _digitos(r, 13))
                if n is None:
                    continue
        elif tipo == "titulo":
            n = dv.completar_titulo(_digitos(r, 8), f"{r.randint(1, 28):02d}")
        elif tipo == "telefone":
            n = r.choice(DDDS) + "9" + _digitos(r, 8)
        else:
            raise ValueError(tipo)
        if positivo_aceitavel(tipo, n):
            return n


# ----------------------------------------------------------------- frases-modelo

FRASES_DOCUMENTO = {
    "cpf": ["Meu CPF é {}.", "Segue o CPF do titular: {}.", "Pode conferir pelo número {}?"],
    "cnpj": ["O CNPJ da empresa é {}.", "Faturar para o CNPJ {}, por favor.", "Cadastro da loja: {}."],
    "cns": ["Meu cartão do SUS é {}.", "Número do cartão de saúde: {}.", "Anotei aqui o número {}."],
    "pis": ["Meu PIS é {}.", "O NIT informado foi {}.", "Consta o número {} no cadastro."],
    "titulo": ["Meu título de eleitor é {}.", "Título: {}.", "O documento que tenho é o {}."],
}
FRASES_OUTRO_IDENTIFICADOR = [
    "O protocolo do atendimento é {}.",
    "A nota fiscal saiu com o número {}.",
    "Código do pedido: {}.",
    "Me passaram o rastreio {}, ainda não atualizou.",
]
FRASES_VALOR = [
    "O valor total ficou em R$ {}.",
    "Foi cobrado R$ {} na fatura, não reconheço.",
    "O orçamento veio de R$ {}.",
]
FRASES_TELEFONE = ["Pode me ligar no {}.", "Meu celular é {}.", "WhatsApp para contato: {}."]
FRASES_HORARIO = ["O atendimento funciona das {}.", "A entrega foi agendada para as {}.", "Posso receber na faixa das {}."]
FRASES_CODIGO = ["Código da reserva: {}.", "No boleto aparece a sequência {}.", "O número do lote é {}."]
FRASES_EMAIL = ["Meu e-mail é {}.", "Envie a segunda via para {}.", "Pode responder em {}."]
FRASES_ARROBA = ["Me marca no {} quando postar.", "O anexo se chama {}.", "Segue a gente no {}."]


# ---------------------------------------------------------------- ocorrencias

def _ocorrencia(r, frases, tipo, valor, polaridade, classe=None, atributos=None) -> dict:
    return {
        "frase": r.choice(frases),
        "tipo": tipo,
        "valor": valor,
        "polaridade": polaridade,
        "classe_negativo": classe,
        "natureza": NATUREZA[tipo],
        "atributos": atributos or {},
    }


def positivos(r: random.Random, tipo: str) -> list[dict]:
    saida = []
    for i in range(POSITIVOS_POR_TIPO):
        if tipo == "email":
            local = "".join(r.choice(string.ascii_lowercase) for _ in range(r.randint(4, 10)))
            valor = f"{local}{r.choice(['', '.', '_'])}{_digitos(r, r.randint(0, 3))}@{r.choice(DOMINIOS)}"
            saida.append(_ocorrencia(r, FRASES_EMAIL, tipo, valor, "positivo"))
            continue
        if tipo == "telefone":
            valor = formatar_telefone(nucleo_positivo(r, tipo), i, r)
            saida.append(_ocorrencia(r, FRASES_TELEFONE, tipo, valor, "positivo",
                                     atributos={"formato": i % FORMATOS_TELEFONE}))
            continue
        alfa = tipo == "cnpj" and i % 2 == 1
        n = nucleo_positivo(r, tipo, alfanumerico=alfa)
        formato = FORMATOS_MASCARA[i % 3]
        if formato == "completa":
            valor = mascarar(tipo, n)
        elif formato == "ausente":
            valor = n
        else:
            valor = mascarar_parcial(r, tipo, n)
        atributos = {"mascara": formato}
        if tipo == "cnpj":
            atributos["formato_cnpj"] = "alfanumerico" if alfa else "numerico"
        saida.append(_ocorrencia(r, FRASES_DOCUMENTO[tipo], tipo, valor, "positivo", atributos=atributos))
    return saida


def _negativo_n1(r, tipo, alfa, parcial=False):
    while True:
        n = nucleo_positivo(r, tipo, alfanumerico=alfa)
        trocado = n[:-1] + str((int(n[-1]) + r.randint(1, 9)) % 10)
        if negativo_aceitavel(trocado):
            return mascarar_parcial(r, tipo, trocado) if parcial else mascarar(tipo, trocado)


def _negativo_n2(r, tipo, alfa):
    comprimento = dv.COMPRIMENTO[tipo]
    alfabeto = string.digits + string.ascii_uppercase if alfa else string.digits
    while True:
        n = "".join(r.choice(alfabeto) for _ in range(comprimento))
        if alfa and n.isdigit():
            continue
        if negativo_aceitavel(n):
            return n


def _negativo_n3(r, tipo, alfa, com_mascara):
    while True:
        n = nucleo_positivo(r, tipo, alfanumerico=alfa)
        if com_mascara:
            m = mascarar(tipo, n)
            posicoes = [i for i, c in enumerate(m) if c.isalnum()]
            p = r.choice(posicoes[-4:])  # falta um caractere no fim, como num numero truncado
            valor = m[:p] + m[p + 1:]
        else:
            p = r.randrange(len(n))
            valor = n[:p] + n[p + 1:]
        if negativo_aceitavel(_so_caracteres(valor)):
            return valor


def _valor_monetario(digitos: str) -> str:
    inteiro, centavos = digitos[:-2].lstrip("0") or "0", digitos[-2:]
    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    return ".".join(grupos) + "," + centavos


def _negativo_n5(r, tipo):
    comprimento = dv.COMPRIMENTO[tipo]
    while True:
        d = r.choice("123456789") + _digitos(r, comprimento - 1)
        if negativo_aceitavel(d):
            return _valor_monetario(d)


def negativos(r: random.Random, tipo: str) -> list[dict]:
    saida = []
    k = POR_CLASSE[tipo]
    if tipo == "telefone":
        for _ in range(k):  # T1: quantidade errada de digitos
            while True:  # 7 ou 10 digitos apos o DDD; confere numero e valor formatado
                nucleo = r.choice(DDDS) + "9" + _digitos(r, r.choice([6, 9]))
                valor = formatar_telefone(nucleo, r.randrange(FORMATOS_TELEFONE), r)
                if negativo_aceitavel(nucleo) and valor_negativo_aceitavel(valor):
                    break
            saida.append(_ocorrencia(r, FRASES_TELEFONE, tipo, valor, "negativo", "T1"))
        fora = [f"{i:02d}" for i in range(11, 100) if f"{i:02d}" not in DDDS and i % 10 != 0]
        for j in range(k):  # T2: parece telefone
            if j % 2 == 0:
                h1, h2 = r.randint(7, 11), r.randint(12, 20)
                valor = f"{h1:02d}:{r.choice(['00', '30'])}-{h2:02d}:{r.choice(['00', '30'])}"
            else:  # mesma pontuacao, DDD inexistente (fora da lista da Anatel)
                while True:  # 11 digitos colide com CPF e PIS/NIT
                    nucleo = r.choice(fora) + "9" + _digitos(r, 8)
                    valor = formatar_telefone(nucleo, 0)
                    if negativo_aceitavel(nucleo) and valor_negativo_aceitavel(valor):
                        break
            frases = FRASES_HORARIO if j % 2 == 0 else FRASES_CODIGO
            saida.append(_ocorrencia(r, frases, tipo, valor, "negativo", "T2"))
        return saida
    if tipo == "email":
        for j in range(k):  # E1: incompleto
            local = "".join(r.choice(string.ascii_lowercase) for _ in range(r.randint(4, 9)))
            valor = f"{local}@" if j % 2 == 0 else f"@{r.choice(DOMINIOS)}"
            saida.append(_ocorrencia(r, FRASES_EMAIL, tipo, valor, "negativo", "E1"))
        for j in range(k):  # E2: arroba que nao e endereco
            palavra = "".join(r.choice(string.ascii_lowercase) for _ in range(r.randint(4, 9)))
            valor = f"@{palavra}" if j % 2 == 0 else f"{palavra}@2x.png"
            saida.append(_ocorrencia(r, FRASES_ARROBA, tipo, valor, "negativo", "E2"))
        return saida

    for j in range(k):
        alfa = tipo == "cnpj" and j % 2 == 1
        parcial = j >= k - N1_PARCIAIS
        valor = _negativo_n1(r, tipo, alfa, parcial)
        saida.append(_ocorrencia(r, FRASES_DOCUMENTO[tipo], tipo, valor, "negativo", "N1",
                                 atributos={"mascara": "parcial" if parcial else "completa"}))
    for j in range(esperado(tipo, "N2")):
        alfa = tipo == "cnpj" and j % 2 == 1
        saida.append(_ocorrencia(r, FRASES_OUTRO_IDENTIFICADOR, tipo, _negativo_n2(r, tipo, alfa), "negativo", "N2"))
    for j in range(k):
        alfa = tipo == "cnpj" and j % 2 == 1
        saida.append(_ocorrencia(r, FRASES_DOCUMENTO[tipo], tipo, _negativo_n3(r, tipo, alfa, j % 2 == 0), "negativo", "N3"))
    repeticoes = [d * dv.COMPRIMENTO[tipo] for d in "0123456789"]
    aceitas = [n for n in repeticoes if negativo_aceitavel(n)]
    assert len(aceitas) == esperado(tipo, "N4"), (tipo, len(aceitas))
    for n in aceitas:  # N4: as repeticoes existentes que sao negativo inequivoco
        d = n[0]
        valor = mascarar(tipo, n) if int(d) % 2 == 0 else n
        saida.append(_ocorrencia(r, FRASES_DOCUMENTO[tipo], tipo, valor, "negativo", "N4"))
    for _ in range(k):
        saida.append(_ocorrencia(r, FRASES_VALOR, tipo, _negativo_n5(r, tipo), "negativo", "N5"))
    return saida


# ----------------------------------------------------------------- montagem

def montar(semente: int) -> list[dict]:
    r = random.Random(semente)
    ocorrencias = []
    for tipo in TIPOS:
        ocorrencias += positivos(r, tipo) + negativos(r, tipo)
    r.shuffle(ocorrencias)

    textos = []
    i = 0
    while i < len(ocorrencias):
        grupo = ocorrencias[i:i + r.randint(1, 3)]
        i += len(grupo)
        partes, gabarito, cursor = [], [], 0
        for o in grupo:
            antes, depois = o["frase"].split("{}")
            if partes:
                partes.append(" ")
                cursor += 1
            inicio = cursor + len(antes)
            partes.append(antes + o["valor"] + depois)
            cursor += len(antes) + len(o["valor"]) + len(depois)
            gabarito.append({k: v for k, v in o.items() if k != "frase"} | {"inicio": inicio, "fim": inicio + len(o["valor"])})
        textos.append({"id": f"pii-{len(textos) + 1:04d}", "texto": "".join(partes), "ocorrencias": gabarito})
    return textos


def conferir(textos: list[dict]) -> collections.Counter:
    contagem = collections.Counter()
    for t in textos:
        for o in t["ocorrencias"]:
            assert t["texto"][o["inicio"]:o["fim"]] == o["valor"], (t["id"], o)
            contagem[(o["tipo"], o["polaridade"], o["classe_negativo"])] += 1
            if o["tipo"] == "email" and o["polaridade"] == "positivo":
                assert o["valor"].split("@")[1] in DOMINIOS
    for tipo in TIPOS:
        assert contagem[(tipo, "positivo", None)] == POSITIVOS_POR_TIPO, tipo
        for classe in CLASSES[tipo]:
            assert contagem[(tipo, "negativo", classe)] == esperado(tipo, classe), (tipo, classe)

    formatos = collections.Counter()
    for t in textos:
        for o in t["ocorrencias"]:
            if o["tipo"] in DOCUMENTOS and (o["polaridade"] == "positivo" or o["classe_negativo"] == "N1"):
                formato = o["atributos"]["mascara"]
                formatos[(o["tipo"], o["polaridade"], formato)] += 1
                if formato == "parcial":
                    nucleo = _so_caracteres(o["valor"])
                    assert o["valor"] != nucleo, o
                    assert o["valor"] != mascarar(o["tipo"], nucleo), o
            if o["tipo"] == "telefone" and o["polaridade"] == "positivo":
                formatos[("telefone", o["atributos"]["formato"])] += 1
    for tipo in DOCUMENTOS:
        for formato, n in CONTAGEM_FORMATOS.items():
            assert formatos[(tipo, "positivo", formato)] == n, (tipo, formato)
        assert formatos[(tipo, "negativo", "parcial")] == N1_PARCIAIS, tipo
    for estilo in range(FORMATOS_TELEFONE):
        assert formatos[("telefone", estilo)] == POSITIVOS_POR_TIPO // FORMATOS_TELEFONE, estilo
    return contagem


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--amostra", type=int, default=0)
    analisador.add_argument("--semente", type=int, default=None)
    argumentos = analisador.parse_args()

    semente = argumentos.semente or int(os.getenv("SEMENTE_MESTRA", "20260829"))
    textos = montar(semente)
    contagem = conferir(textos)
    ocorrencias = sum(contagem.values())

    print(f"semente: {semente}")
    print(f"textos: {len(textos)}; ocorrencias: {ocorrencias}")
    for tipo in TIPOS:
        pos = contagem[(tipo, "positivo", None)]
        neg = {c: contagem[(tipo, "negativo", c)] for c in CLASSES[tipo]}
        print(f"  {tipo:<9} positivos {pos:>3}  negativos {neg}")

    if argumentos.amostra:
        print()
        for t in random.Random(1).sample(textos, argumentos.amostra):
            print(f"[{t['id']}] {t['texto']}")
            for o in t["ocorrencias"]:
                rotulo = o["polaridade"] + (f" {o['classe_negativo']}" if o["classe_negativo"] else "")
                print(f"     {o['inicio']:>3}-{o['fim']:<3} {o['tipo']:<9} {rotulo}")
        print("\nNenhum arquivo gravado.")
        return 0

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    temporario = SAIDA.with_suffix(".tmp")
    with temporario.open("w", encoding="utf-8", newline="\n") as arquivo:
        for t in textos:
            arquivo.write(json.dumps(t, ensure_ascii=False, sort_keys=True) + "\n")
    temporario.replace(SAIDA)
    print(f"gravado: {SAIDA}")
    print(f"sha256: {hashlib.sha256(SAIDA.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
