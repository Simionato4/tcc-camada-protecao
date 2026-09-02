"""Unico ponto do projeto autorizado a chamar o modelo de linguagem.

Toda chamada passa pelo GuardaOrcamento. Em MODO_SIMULADO=1 nenhuma requisicao
sai da maquina: a resposta e sintetica e o consumo e estimado, o que permite
desenvolver e depurar o executor com custo zero.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from executor.orcamento import GuardaOrcamento


@dataclass
class RespostaModelo:
    texto: str
    tokens_entrada: int
    tokens_saida: int
    usd: float
    simulado: bool


def _estimar_tokens(texto: str) -> int:
    """Aproximacao grosseira usada apenas no modo simulado."""
    return max(1, len(texto) // 4)


class ClienteModelo:
    def __init__(self, guarda: GuardaOrcamento | None = None) -> None:
        self.guarda = guarda or GuardaOrcamento()
        self.modelo = os.getenv("MODELO_ID", "claude-haiku-4-5-20251001")
        self.temperatura = float(os.getenv("TEMPERATURA", "0"))
        self.max_tokens = int(os.getenv("MAX_TOKENS_SAIDA", "400"))
        self.simulado = os.getenv("MODO_SIMULADO", "1") == "1"
        if self.simulado != self.guarda.simulado:
            raise RuntimeError(
                "cliente e guarda em modos diferentes: o consumo iria para o livro-caixa "
                f"errado (cliente simulado={self.simulado}, guarda simulado={self.guarda.simulado})"
            )
        self._cliente = None

    def _obter_cliente(self):
        if self._cliente is None:
            from anthropic import Anthropic

            chave = os.getenv("ANTHROPIC_API_KEY")
            if not chave:
                raise RuntimeError("ANTHROPIC_API_KEY nao definida no .env")
            self._cliente = Anthropic(api_key=chave)
        return self._cliente

    def responder(self, *, sistema: str, mensagem: str) -> RespostaModelo:
        self.guarda.antes_de_chamar()

        if self.simulado:
            tokens_entrada = _estimar_tokens(sistema) + _estimar_tokens(mensagem)
            tokens_saida = 150
            usd = self.guarda.registrar(tokens_entrada, tokens_saida)
            return RespostaModelo(
                texto="[SIMULADO] nenhuma chamada real foi feita.",
                tokens_entrada=tokens_entrada,
                tokens_saida=tokens_saida,
                usd=usd,
                simulado=True,
            )

        resposta = self._obter_cliente().messages.create(
            model=self.modelo,
            max_tokens=self.max_tokens,
            temperature=self.temperatura,
            system=sistema,
            messages=[{"role": "user", "content": mensagem}],
        )
        tokens_entrada = resposta.usage.input_tokens
        tokens_saida = resposta.usage.output_tokens
        usd = self.guarda.registrar(tokens_entrada, tokens_saida)
        texto = "".join(bloco.text for bloco in resposta.content if bloco.type == "text")
        return RespostaModelo(
            texto=texto,
            tokens_entrada=tokens_entrada,
            tokens_saida=tokens_saida,
            usd=usd,
            simulado=False,
        )
