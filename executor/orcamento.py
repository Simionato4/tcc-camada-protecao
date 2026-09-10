"""Guarda de orcamento da API.

Motivo de existir: o credito e finito (US$ 20) e um laco mal fechado inviabiliza
o trabalho. Nenhuma chamada ao modelo pode ser feita fora daqui.

Quatro protecoes independentes:
  1. teto de chamadas       - impede laco infinito
  2. teto em dolares        - impede laco caro com poucas chamadas
  3. reserva previa         - recusa a chamada cujo custo estimado ultrapassaria o
                              teto, em vez de so constatar o estouro depois
  4. modo simulado          - permite desenvolver o executor sem gastar nada

O teto em dolares e o limite que de fato importa; o teto de chamadas existe apenas
como guarda contra laco infinito, e por isso e folgado o suficiente para nao
impedir uma reexecucao completa do protocolo.

O consumo e persistido em disco, entao o teto vale para a soma de todas as
execucoes, e nao para cada processo isolado.

Modo simulado e modo real gravam em ARQUIVOS SEPARADOS. Sem essa separacao, as
dezenas de execucoes de depuracao inflariam o consumo registrado, o teto poderia
disparar por gasto inexistente, e o livro-caixa que vai para docs/orcamento.md
deixaria de refletir dolares reais.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


class OrcamentoExcedido(RuntimeError):
    """Levantada antes da chamada, nunca depois. O gasto nao acontece."""


@dataclass
class Consumo:
    chamadas: int = 0
    tokens_entrada: int = 0
    tokens_saida: int = 0
    usd: float = 0.0

    def como_dicionario(self) -> dict:
        return {
            "chamadas": self.chamadas,
            "tokens_entrada": self.tokens_entrada,
            "tokens_saida": self.tokens_saida,
            "usd": round(self.usd, 6),
        }


class GuardaOrcamento:
    def __init__(
        self,
        *,
        teto_chamadas: int | None = None,
        teto_usd: float | None = None,
        arquivo: str | None = None,
        preco_entrada_usd_mtok: float | None = None,
        preco_saida_usd_mtok: float | None = None,
        simulado: bool | None = None,
        custo_estimado_chamada: float | None = None,
    ) -> None:
        self.simulado = (
            simulado if simulado is not None else os.getenv("MODO_SIMULADO", "1") == "1"
        )
        self.teto_chamadas = teto_chamadas or int(os.getenv("TETO_CHAMADAS", "4500"))
        self.teto_usd = teto_usd or float(os.getenv("TETO_USD", "16.00"))
        self.preco_entrada = preco_entrada_usd_mtok or float(
            os.getenv("PRECO_ENTRADA_USD_MTOK", "1.0")
        )
        self.preco_saida = preco_saida_usd_mtok or float(
            os.getenv("PRECO_SAIDA_USD_MTOK", "5.0")
        )
        self.custo_estimado_chamada = custo_estimado_chamada or float(
            os.getenv("CUSTO_ESTIMADO_CHAMADA_USD", "0.0025")
        )
        self.arquivo = self._caminho(
            arquivo or os.getenv("ARQUIVO_CONSUMO", "resultados/consumo.json")
        )
        self.consumo = self._carregar()

    def _caminho(self, bruto: str) -> Path:
        """Acrescenta o sufixo -simulado quando nenhuma chamada real e feita."""
        caminho = Path(bruto)
        if self.simulado:
            return caminho.with_name(f"{caminho.stem}-simulado{caminho.suffix}")
        return caminho

    def _carregar(self) -> Consumo:
        if self.arquivo.exists():
            dados = json.loads(self.arquivo.read_text(encoding="utf-8"))
            return Consumo(**dados)
        return Consumo()

    def _gravar(self) -> None:
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        self.arquivo.write_text(
            json.dumps(self.consumo.como_dicionario(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def antes_de_chamar(self) -> None:
        """Verifica os tres limites ANTES da chamada. O gasto nunca acontece aqui.

        A reserva usa uma estimativa conservadora do custo da proxima chamada, em
        vez de apenas constatar que o teto ja foi ultrapassado. Sem ela, a ultima
        chamada de uma execucao longa poderia estourar o teto por um valor que
        ninguem autorizou.
        """
        if self.consumo.chamadas >= self.teto_chamadas:
            raise OrcamentoExcedido(
                f"teto de chamadas atingido: {self.consumo.chamadas}/{self.teto_chamadas}"
            )
        projetado = self.consumo.usd + self.custo_estimado_chamada
        if projetado > self.teto_usd:
            raise OrcamentoExcedido(
                f"reserva recusada: consumo {self.consumo.usd:.4f} mais estimativa "
                f"{self.custo_estimado_chamada:.4f} ultrapassaria o teto de "
                f"{self.teto_usd:.2f}"
            )

    def custo(self, tokens_entrada: int, tokens_saida: int) -> float:
        return (
            tokens_entrada / 1_000_000 * self.preco_entrada
            + tokens_saida / 1_000_000 * self.preco_saida
        )

    def registrar(self, tokens_entrada: int, tokens_saida: int) -> float:
        gasto = self.custo(tokens_entrada, tokens_saida)
        self.consumo.chamadas += 1
        self.consumo.tokens_entrada += tokens_entrada
        self.consumo.tokens_saida += tokens_saida
        self.consumo.usd += gasto
        self._gravar()
        return gasto

    def restante(self) -> dict:
        return {
            "chamadas_restantes": self.teto_chamadas - self.consumo.chamadas,
            "usd_restante": round(self.teto_usd - self.consumo.usd, 4),
            # A tolerancia evita que aritmetica de ponto flutuante devolva 399
            # onde o valor exato e 400.
            "chamadas_cabendo_no_teto_usd": int(
                max(0.0, self.teto_usd - self.consumo.usd) / self.custo_estimado_chamada
                + 1e-9
            ),
        }
