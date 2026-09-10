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
        simulado=False,
        custo_estimado_chamada=0.0,
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
    with pytest.raises(OrcamentoExcedido, match="reserva recusada"):
        g.antes_de_chamar()


def test_reserva_recusa_chamada_que_estouraria_o_teto(tmp_path):
    """O guarda recusa ANTES, e nao constata o estouro depois.

    Sem a reserva, a ultima chamada de uma execucao longa gastaria um valor que
    nenhum teto autorizou, porque a verificacao so olhava o consumo ja ocorrido.
    """
    g = guarda(tmp_path, teto_chamadas=1000, teto_usd=1.0, custo_estimado_chamada=0.30)
    for _ in range(3):
        g.antes_de_chamar()
        g.registrar(200_000, 0)  # US$ 0,20 por chamada, consumo chega a 0,60
    # consumo 0,60 esta abaixo do teto, mas 0,60 + 0,30 de reserva ultrapassaria 1,00?
    g.antes_de_chamar()  # 0,90 ainda cabe
    g.registrar(200_000, 0)  # consumo vai a 0,80
    with pytest.raises(OrcamentoExcedido, match="reserva recusada"):
        g.antes_de_chamar()  # 0,80 + 0,30 = 1,10 nao cabe
    assert g.consumo.usd < g.teto_usd  # o teto nunca foi ultrapassado de fato


def test_restante_informa_quantas_chamadas_ainda_cabem(tmp_path):
    g = guarda(tmp_path, teto_chamadas=10_000, teto_usd=1.0, custo_estimado_chamada=0.0025)
    assert g.restante()["chamadas_cabendo_no_teto_usd"] == 400


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
    cliente = ClienteModelo(guarda(tmp_path, teto_chamadas=10, simulado=True))
    resposta = cliente.responder(sistema="s", mensagem="m")
    assert resposta.simulado is True
    assert cliente._cliente is None  # nenhum cliente HTTP foi sequer construido


def test_simulado_e_real_gravam_em_arquivos_separados(tmp_path):
    """Execucao de depuracao nao pode inflar o consumo real.

    Sem essa separacao, as dezenas de rodadas simuladas da Etapa 5 fariam o teto
    em dolares disparar por gasto que nunca existiu.
    """
    base = str(tmp_path / "consumo.json")
    simulado = guarda(tmp_path, arquivo=base, simulado=True)
    real = guarda(tmp_path, arquivo=base, simulado=False)

    assert simulado.arquivo.name == "consumo-simulado.json"
    assert real.arquivo.name == "consumo.json"

    simulado.registrar(1000, 1000)
    assert guarda(tmp_path, arquivo=base, simulado=False).consumo.chamadas == 0
    assert guarda(tmp_path, arquivo=base, simulado=True).consumo.chamadas == 1


def test_cliente_recusa_guarda_em_modo_divergente(tmp_path, monkeypatch):
    from executor.cliente_modelo import ClienteModelo

    monkeypatch.setenv("MODO_SIMULADO", "1")
    with pytest.raises(RuntimeError, match="modos diferentes"):
        ClienteModelo(guarda(tmp_path, simulado=False))
