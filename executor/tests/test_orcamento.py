"""O guarda de orcamento e a peca que impede o trabalho de ficar inviavel.
Ele merece teste antes de qualquer outra coisa do executor.
"""

import pytest

from executor.orcamento import GuardaOrcamento, OrcamentoExcedido


def guarda(tmp_path, **kwargs):
    padrao = dict(
        teto_chamadas=3,
        teto_usd=1.0,
        arquivo=str(tmp_path / "consumo.json"),
        preco_entrada_usd_mtok=1.0,
        preco_saida_usd_mtok=5.0,
    )
    padrao.update(kwargs)
    return GuardaOrcamento(**padrao)


def test_custo_usa_os_precos_configurados(tmp_path):
    g = guarda(tmp_path)
    assert g.custo(1_000_000, 0) == pytest.approx(1.0)
    assert g.custo(0, 1_000_000) == pytest.approx(5.0)


def test_teto_de_chamadas_interrompe_antes_de_gastar(tmp_path):
    g = guarda(tmp_path)
    for _ in range(3):
        g.antes_de_chamar()
        g.registrar(10, 10)
    with pytest.raises(OrcamentoExcedido, match="teto de chamadas"):
        g.antes_de_chamar()


def test_teto_em_dolares_interrompe_antes_de_gastar(tmp_path):
    g = guarda(tmp_path, teto_chamadas=1000, teto_usd=0.01)
    g.antes_de_chamar()
    g.registrar(1_000_000, 0)  # US$ 1,00, muito acima do teto
    with pytest.raises(OrcamentoExcedido, match="teto em dolares"):
        g.antes_de_chamar()


def test_consumo_persiste_entre_processos(tmp_path):
    arquivo = str(tmp_path / "consumo.json")
    primeiro = guarda(tmp_path, arquivo=arquivo)
    primeiro.registrar(100, 100)
    segundo = guarda(tmp_path, arquivo=arquivo)
    assert segundo.consumo.chamadas == 1
    assert segundo.consumo.tokens_entrada == 100


def test_modo_simulado_nao_chama_a_api(tmp_path, monkeypatch):
    from executor.cliente_modelo import ClienteModelo

    monkeypatch.setenv("MODO_SIMULADO", "1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cliente = ClienteModelo(guarda(tmp_path, teto_chamadas=10))
    resposta = cliente.responder(sistema="s", mensagem="m")
    assert resposta.simulado is True
    assert cliente._cliente is None  # nenhum cliente HTTP foi sequer construido
