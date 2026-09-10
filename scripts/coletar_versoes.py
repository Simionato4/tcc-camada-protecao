"""Tarefa 0.10: coleta a versao real de cada componente, por comando.

Gera um bloco pronto para colar em docs/versoes.md. Nao anote versao de memoria:
o que vale e o que a maquina responde.

Uso:  python scripts/coletar_versoes.py
"""

import subprocess
import sys
from datetime import date

COMANDOS = [
    ("Windows", ["cmd", "/c", "ver"]),
    ("WSL", ["wsl", "--version"]),
    ("Docker", ["docker", "--version"]),
    ("Docker Compose", ["docker", "compose", "version"]),
    ("Python", [sys.executable, "--version"]),
    ("Git", ["git", "--version"]),
    ("Spec Kit", ["specify", "--version"]),
]

IMAGENS = [
    "docker.n8n.io/n8nio/n8n:latest",
    "qdrant/qdrant:latest",
    "ghcr.io/data-privacy-stack/presidio-analyzer:latest",
    "ghcr.io/data-privacy-stack/presidio-anonymizer:latest",
    "python:3.12-slim",
]


def executar(comando: list[str]) -> str:
    try:
        saida = subprocess.run(comando, capture_output=True, text=True, timeout=60)
        return (saida.stdout + saida.stderr).strip().splitlines()[0]
    except Exception as erro:  # noqa: BLE001
        return f"NAO OBTIDO ({type(erro).__name__})"


def main() -> None:
    print(f"# Versoes - coletado em {date.today().isoformat()}\n")
    print("## Ferramentas\n")
    print("| Componente | Versao |")
    print("|---|---|")
    for nome, comando in COMANDOS:
        print(f"| {nome} | {executar(comando)} |")

    print("\n## Imagens de conteiner (digest)\n")
    print("Cole cada digest na tag da imagem em docker-compose.yml, no lugar de `latest`.\n")
    print("| Imagem | Digest |")
    print("|---|---|")
    for imagem in IMAGENS:
        digest = executar(
            ["docker", "image", "inspect", imagem, "--format", "{{index .RepoDigests 0}}"]
        )
        print(f"| {imagem} | {digest} |")


if __name__ == "__main__":
    main()
