"""Registro estruturado, um evento JSON por linha.

Nesta etapa o texto NAO e gravado, nem em parte: o log guarda apenas o tamanho e
um resumo criptografico. Isso satisfaz por construcao a exigencia de que a camada
mascare dados pessoais nos proprios registros, ate a Etapa 4 implementar o
mascaramento de verdade.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _resumo(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


class Registrador:
    def __init__(self, caminho: str | None = None) -> None:
        self.caminho = Path(caminho) if caminho else None
        if self.caminho:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)

    def evento(self, **campos: object) -> None:
        linha = {
            "instante": datetime.now(timezone.utc).isoformat(),
            **campos,
        }
        serializado = json.dumps(linha, ensure_ascii=False)
        print(serializado, file=sys.stdout, flush=True)
        if self.caminho:
            with self.caminho.open("a", encoding="utf-8") as arquivo:
                arquivo.write(serializado + "\n")

    def requisicao_processada(
        self,
        *,
        id_requisicao: str,
        ponto: str,
        condicao: str,
        texto_entrada: str,
        texto_saida: str,
        decisao: str,
        quantidade_deteccoes: int,
        tempo_ms: float,
        versao_regras: str,
    ) -> None:
        self.evento(
            evento="requisicao_processada",
            id_requisicao=id_requisicao,
            ponto=ponto,
            condicao=condicao,
            resumo_entrada=_resumo(texto_entrada),
            tamanho_entrada=len(texto_entrada),
            resumo_saida=_resumo(texto_saida),
            tamanho_saida=len(texto_saida),
            decisao=decisao,
            quantidade_deteccoes=quantidade_deteccoes,
            tempo_ms=tempo_ms,
            versao_regras=versao_regras,
        )


registrador = Registrador(os.getenv("ARQUIVO_LOG", "resultados/camada.jsonl"))
