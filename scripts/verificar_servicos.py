"""Tarefa 0.9: prova que os cinco servicos responderam.

Uso:  python scripts/verificar_servicos.py
Nao depende de nada instalado alem da biblioteca padrao.
"""

import json
import sys
import urllib.error
import urllib.request

SERVICOS = [
    ("n8n", "GET", "http://localhost:5678/healthz", None),
    ("qdrant", "GET", "http://localhost:6333/collections", None),
    (
        "presidio-analyzer",
        "POST",
        "http://localhost:5002/analyze",
        {"text": "meu nome e Joao", "language": "en"},
    ),
    (
        "presidio-anonymizer",
        "POST",
        "http://localhost:5001/anonymize",
        {"text": "meu nome e Joao", "analyzer_results": []},
    ),
    ("camada", "GET", "http://localhost:8000/saude", None),
]


def consultar(metodo: str, url: str, corpo: dict | None) -> tuple[int, str]:
    dados = json.dumps(corpo).encode() if corpo is not None else None
    cabecalhos = {"Content-Type": "application/json"} if dados else {}
    requisicao = urllib.request.Request(url, data=dados, headers=cabecalhos, method=metodo)
    with urllib.request.urlopen(requisicao, timeout=15) as resposta:
        return resposta.status, resposta.read().decode()[:120]


def main() -> int:
    falhas = 0
    for nome, metodo, url, corpo in SERVICOS:
        try:
            status, trecho = consultar(metodo, url, corpo)
            print(f"[ok]    {nome:22} {status}  {trecho}")
        except urllib.error.HTTPError as erro:
            print(f"[HTTP]  {nome:22} {erro.code}  {erro.reason}")
            falhas += 1
        except Exception as erro:  # noqa: BLE001
            print(f"[falha] {nome:22} {type(erro).__name__}: {erro}")
            falhas += 1
    print()
    print("TODOS OS SERVICOS RESPONDERAM" if falhas == 0 else f"{falhas} servico(s) sem resposta")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
