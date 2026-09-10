"""Carrega o prompt de sistema versionado.

O prompt e **variavel de controle**: identico nas quatro condicoes. Por isso ele e
carregado pelo servico, e nao enviado por quem chama. Se o fluxo do assistente
pudesse informar o prompt, bastaria um erro de configuracao para que uma condicao
rodasse com prompt diferente das outras, e a comparacao perderia sentido sem que
nada acusasse.
"""

from pathlib import Path


def extrair_texto(conteudo: str) -> str:
    """Devolve o bloco de codigo do arquivo, que e o prompt que vai para a API.

    O arquivo carrega documentacao ao redor do texto — a declaracao de que o
    marcador nao e segredo, a vantagem estrutural da camada, a severidade pela
    escala do LLM08. Nada disso vai para o modelo.
    """
    partes = conteudo.split("```")
    if len(partes) < 3:
        raise ValueError("bloco do prompt nao encontrado no arquivo")
    return partes[1].strip()


def carregar_prompt(caminho: Path) -> str:
    return extrair_texto(caminho.read_bytes().decode("utf-8"))
