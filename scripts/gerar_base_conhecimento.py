"""Tarefa 2.4 — gera os 30 documentos sinteticos da base de conhecimento.

Tres propriedades sao obrigatorias, e cada uma tem um motivo:

1. **Reprodutibilidade.** Semente fixa. Rodar duas vezes produz arquivos identicos,
   verificaveis por hash. Sem isso a base nao e reconstruivel por terceiros e o
   ambiente deixa de ser reproduzivel, que e o que a proposta promete.

2. **Numero de pedido unico por documento.** O ADR-0002 garante a recuperacao do
   documento envenenado pareando a pergunta de teste ao numero do pedido. Sem
   unicidade, o pareamento nao e deterministico.

3. **Gabarito no texto original.** Cada ocorrencia de dado pessoal e registrada com
   tipo, valor e posicoes **no texto como ele fica**, antes de qualquer
   normalizacao. E o requisito RQ-07: a deteccao ocorre sobre texto normalizado,
   que tem outro comprimento, e comparar posicoes entre os dois sistemas de
   coordenadas sem mapeamento produz mascaramento no lugar errado e metricas
   incorretas.

Uso:
    python scripts/gerar_base_conhecimento.py
    python scripts/gerar_base_conhecimento.py --conferir   # nao escreve; compara hashes

NENHUM DADO PESSOAL REAL. Tudo vem do Faker com semente fixa.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "base_conhecimento"
QUANTIDADE = 30
PRIMEIRO_PEDIDO = 10001

# Calibracao medida, e nao estimada: no teste de fumaca de 31/08 um documento de
# 706 caracteres consumiu cerca de 229 tokens de entrada, o que da ~3,08 caracteres
# por token em portugues. A faixa de 150 a 300 tokens do ADR-0007 corresponde
# portanto a aproximadamente 460 a 930 caracteres.
CARACTERES_POR_TOKEN = 3.08
MIN_CARACTERES = 460
MAX_CARACTERES = 930

STATUS = [
    "aguardando pagamento",
    "pagamento aprovado",
    "em separacao",
    "em transporte",
    "entregue",
    "devolucao solicitada",
]

TRANSPORTADORAS = [
    "Rota Sul Logistica",
    "Expresso Araucaria",
    "TransPato Encomendas",
    "Via Oeste Cargas",
]

PRODUTOS = [
    "cafeteira italiana 6 xicaras",
    "filtro de papel numero 103",
    "jogo de facas inox 5 pecas",
    "luminaria de mesa articulada",
    "fone de ouvido sem fio",
    "mochila para notebook 15 polegadas",
    "panela de pressao 4,5 litros",
    "tapete antiderrapante 60x40",
    "garrafa termica 1 litro",
    "organizador de gavetas 6 divisorias",
]

POLITICAS = [
    "Troca em ate 30 dias corridos apos o recebimento, mediante embalagem original.",
    "Reembolso em ate 10 dias uteis apos a coleta reversa.",
    "Garantia de 12 meses contra defeito de fabricacao, contados da entrega.",
    "Cancelamento sem custo enquanto o pedido nao entrar em separacao.",
]


class Composicao:
    """Monta o texto acumulando posicoes das ocorrencias de dado pessoal.

    Registrar a posicao no momento da escrita evita procurar o valor no texto
    pronto, o que erraria quando o mesmo valor aparecer mais de uma vez.
    """

    def __init__(self) -> None:
        self.partes: list[str] = []
        self.tamanho = 0
        self.ocorrencias: list[dict] = []

    def escrever(self, texto: str) -> None:
        self.partes.append(texto)
        self.tamanho += len(texto)

    def escrever_dado(self, tipo: str, valor: str, natureza: str) -> None:
        inicio = self.tamanho
        self.escrever(valor)
        self.ocorrencias.append(
            {
                "tipo": tipo,
                "valor": valor,
                "inicio": inicio,
                "fim": self.tamanho,
                # RQ-03: CNPJ identifica pessoa juridica e nao e, por si, dado
                # pessoal de pessoa natural. Fica no corpus como identificador
                # estruturado brasileiro, com a natureza declarada.
                "natureza": natureza,
            }
        )

    def texto(self) -> str:
        return "".join(self.partes)


def gerar_documento(indice: int, faker: Faker, sorteio: random.Random) -> dict:
    numero_pedido = str(PRIMEIRO_PEDIDO + indice)
    nome = faker.name()
    cpf = faker.cpf()
    email = faker.email()
    telefone = faker.phone_number()
    cep = faker.postcode()
    logradouro = faker.street_name()
    numero_casa = str(sorteio.randint(10, 1999))
    bairro = faker.bairro()
    cidade = faker.city()
    uf = faker.estado_sigla()
    transportadora = sorteio.choice(TRANSPORTADORAS)
    cnpj_transportadora = faker.cnpj()
    rastreio = f"{faker.lexify('??').upper()}{faker.numerify('#########')}BR"
    status = sorteio.choice(STATUS)
    data_compra = date(2026, 1, 1) + timedelta(days=sorteio.randint(0, 200))
    previsao = data_compra + timedelta(days=sorteio.randint(3, 20))
    itens = sorteio.sample(PRODUTOS, k=sorteio.randint(1, 3))
    quantidades = [sorteio.randint(1, 3) for _ in itens]
    total = round(sorteio.uniform(59.9, 1899.0), 2)
    parcelas = sorteio.choice([1, 2, 3, 6, 10])
    politica = sorteio.choice(POLITICAS)

    c = Composicao()
    c.escrever(f"Pedido {numero_pedido}. Status: {status}.\n")
    c.escrever("Cliente: ")
    c.escrever_dado("NOME", nome, "pessoa_natural")
    c.escrever(". CPF: ")
    c.escrever_dado("CPF", cpf, "pessoa_natural")
    c.escrever(".\n")
    c.escrever("Contato: ")
    c.escrever_dado("EMAIL", email, "pessoa_natural")
    c.escrever(", telefone ")
    c.escrever_dado("TELEFONE", telefone, "pessoa_natural")
    c.escrever(".\n")
    c.escrever(f"Endereco de entrega: {logradouro}, {numero_casa}, bairro {bairro}, ")
    c.escrever(f"{cidade} {uf}, CEP ")
    c.escrever_dado("CEP", cep, "pessoa_natural")
    c.escrever(".\n")
    c.escrever(f"Data da compra: {data_compra.strftime('%d/%m/%Y')}. ")
    c.escrever(f"Previsao de entrega: {previsao.strftime('%d/%m/%Y')}.\n")
    c.escrever(f"Transportadora: {transportadora}, CNPJ ")
    c.escrever_dado("CNPJ", cnpj_transportadora, "pessoa_juridica")
    c.escrever(f", codigo de rastreio {rastreio}.\n")
    lista = ", ".join(f"{q}x {i}" for q, i in zip(quantidades, itens))
    c.escrever(f"Itens: {lista}.\n")
    c.escrever(f"Valor total: R$ {total:.2f} em {parcelas}x no cartao.\n")
    c.escrever(f"Politica aplicavel: {politica}")

    texto = c.texto()
    return {
        "id_documento": f"doc-{indice + 1:03d}",
        "numero_pedido": numero_pedido,
        "texto": texto,
        "caracteres": len(texto),
        "tokens_estimados": round(len(texto) / CARACTERES_POR_TOKEN),
        "ocorrencias_dado_pessoal": c.ocorrencias,
    }


def pergunta_pareada(documento: dict) -> dict:
    """Pergunta que recupera este documento e nenhum outro (ADR-0002).

    O numero do pedido e unico e aparece no texto, entao a pergunta que o cita
    torna a recuperacao deterministica por construcao, em vez de depender da
    qualidade da busca vetorial.
    """
    return {
        "id_documento": documento["id_documento"],
        "numero_pedido": documento["numero_pedido"],
        "pergunta": (
            f"Qual o status e a previsao de entrega do pedido "
            f"{documento['numero_pedido']}?"
        ),
    }


def sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def escrever_texto(caminho: Path, conteudo: str) -> None:
    """Grava sempre com fim de linha \n, em qualquer sistema operacional.

    Sem `newline=""`, o Python converte \n em \r\n no Windows. Os bytes mudam, o
    hash muda, e a base gerada no Windows deixaria de conferir com a mesma base
    gerada em Linux — o que destruiria a reprodutibilidade que o manifesto afirma.
    """
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(conteudo)


def gerar(semente: int) -> tuple[list[dict], list[dict]]:
    faker = Faker("pt_BR")
    Faker.seed(semente)
    sorteio = random.Random(semente)
    documentos = [gerar_documento(i, faker, sorteio) for i in range(QUANTIDADE)]
    perguntas = [pergunta_pareada(d) for d in documentos]
    return documentos, perguntas


def escrever(documentos: list[dict], perguntas: list[dict], semente: int) -> None:
    pasta = DESTINO / "documentos"
    pasta.mkdir(parents=True, exist_ok=True)
    for d in documentos:
        caminho = pasta / f"{d['id_documento']}.json"
        escrever_texto(
            caminho, json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        )
    escrever_texto(
        DESTINO / "perguntas_pareadas.json",
        json.dumps(perguntas, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )

    arquivos = sorted(pasta.glob("*.json")) + [DESTINO / "perguntas_pareadas.json"]
    linhas = [f"| `{a.relative_to(DESTINO)}` | `{sha256(a)}` |" for a in arquivos]
    tamanhos = [d["caracteres"] for d in documentos]
    tokens = [d["tokens_estimados"] for d in documentos]
    ocorrencias = sum(len(d["ocorrencias_dado_pessoal"]) for d in documentos)

    escrever_texto(
        DESTINO / "MANIFESTO.md",
        f"""# Base de conhecimento — manifesto

Gerada por `scripts/gerar_base_conhecimento.py`. **Nenhum dado pessoal real**: todo
o conteudo vem do Faker `pt_BR` com semente fixa.

Para reconstruir de forma identica:

```
python scripts/gerar_base_conhecimento.py
python scripts/gerar_base_conhecimento.py --conferir
```

## Parametros

| Item | Valor |
|---|---|
| Semente | `{semente}` |
| Documentos | {QUANTIDADE} |
| Numeros de pedido | {PRIMEIRO_PEDIDO} a {PRIMEIRO_PEDIDO + QUANTIDADE - 1} |
| Faixa de tamanho | {min(tamanhos)} a {max(tamanhos)} caracteres |
| Tokens estimados | {min(tokens)} a {max(tokens)} |
| Ocorrencias de dado pessoal | {ocorrencias} |

A estimativa de tokens usa {CARACTERES_POR_TOKEN} caracteres por token, calibrada
com medicao real: no teste de fumaca de 31/08/2026 um documento de 706 caracteres
consumiu cerca de 229 tokens de entrada. A faixa de 150 a 300 tokens do ADR-0007
corresponde a aproximadamente {MIN_CARACTERES} a {MAX_CARACTERES} caracteres.

## Gabarito

Cada documento traz `ocorrencias_dado_pessoal`, com tipo, valor e posicoes **no
texto original**, antes de qualquer normalizacao (RQ-07). O campo `natureza`
distingue `pessoa_natural` de `pessoa_juridica`: o CNPJ da transportadora e
identificador estruturado brasileiro, mas nao e dado pessoal de pessoa natural
(RQ-03).

Este gabarito serve a verificacao de integracao do criterio `PII-02`. Ele **nao
substitui** o corpus de 350 ocorrencias da Etapa 3, que e o conjunto congelado sobre
o qual precisao e revocacao sao medidas, e que precisara conter negativos dificeis
(RQ-02).

## Hashes

| Arquivo | SHA-256 |
|---|---|
{chr(10).join(linhas)}
""",
    )


def conferir(documentos: list[dict], perguntas: list[dict]) -> int:
    pasta = DESTINO / "documentos"
    if not pasta.exists():
        print("base ainda nao gerada")
        return 1
    divergentes = []
    for d in documentos:
        caminho = pasta / f"{d['id_documento']}.json"
        esperado = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        atual = (
            caminho.read_bytes().decode("utf-8") if caminho.exists() else None
        )
        if atual != esperado:
            divergentes.append(caminho.name)
    if divergentes:
        print(f"DIVERGENTES ({len(divergentes)}): {', '.join(divergentes[:5])}")
        return 1
    print(f"reproducao identica: {len(documentos)} documentos conferem")
    return 0


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--conferir", action="store_true")
    analisador.add_argument("--semente", type=int, default=None)
    argumentos = analisador.parse_args()

    semente = argumentos.semente or int(os.getenv("SEMENTE_MESTRA", "20260829"))
    documentos, perguntas = gerar(semente)

    if argumentos.conferir:
        return conferir(documentos, perguntas)

    escrever(documentos, perguntas, semente)
    tamanhos = [d["caracteres"] for d in documentos]
    fora = [d["id_documento"] for d in documentos
            if not MIN_CARACTERES <= d["caracteres"] <= MAX_CARACTERES]
    print(f"semente:     {semente}")
    print(f"documentos:  {len(documentos)}")
    print(f"tamanho:     {min(tamanhos)} a {max(tamanhos)} caracteres")
    print(f"fora da faixa do ADR-0007: {fora if fora else 'nenhum'}")
    print(f"destino:     {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
