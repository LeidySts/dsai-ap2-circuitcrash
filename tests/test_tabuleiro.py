from circuitcrash.domain import tabuleiro as t


def test_girar_quatro_vezes_volta_ao_inicio() -> None:
    assert t.girar("NE", 4) == "NE"
    assert t.girar("NE") == "ES"
    assert t.girar("NS") == "EW"


def test_partida_demo_comeca_com_lia_e_bruno_energizados() -> None:
    estado = t.nova_partida()
    energizados = [t.circuito_do_jogador(estado, i)[1] for i in range(4)]
    assert energizados == [False, True, True, False]


def test_colocar_curva_energiza_e_captura_bateria() -> None:
    estado = t.nova_partida()
    assert t.jogar_na_casa(estado, 2, 3)
    assert t.circuito_do_jogador(estado, 0)[1]
    assert estado.pontos[0] == 4 + 3
    assert estado.rodada == 7


def test_peca_solta_e_recusada() -> None:
    estado = t.nova_partida()
    assert not t.jogar_na_casa(estado, 5, 5)
    assert estado.erro
    assert estado.rodada == 6


def test_casa_ocupada_por_objetivo_e_recusada() -> None:
    estado = t.nova_partida()
    assert not t.jogar_na_casa(estado, 1, 4)


def test_girar_peca_adversaria_corta_energia() -> None:
    estado = t.nova_partida()
    assert t.jogar_na_casa(estado, 3, 4)  # gira a curva da Lia
    assert not t.circuito_do_jogador(estado, 1)[1]


def test_partida_termina_depois_da_rodada_12() -> None:
    estado = t.nova_partida()
    for _ in range(t.MAX_RODADAS):
        t.passar(estado)
    assert estado.terminou
    assert [c for c, _, _ in t.classificacao(estado)] == [1, 2, 3, 4]


def test_mesma_semente_mesma_mao() -> None:
    assert [p.saidas for p in t.nova_partida().mao] == [p.saidas for p in t.nova_partida().mao]


CARTAS = {"isolante", "ponte", "curto"}


def test_cada_jogador_comeca_com_as_tres_cartas() -> None:
    estado = t.nova_partida()
    assert len(estado.cartas) == 4
    for cartas_do_jogador in estado.cartas:
        assert cartas_do_jogador == CARTAS


def test_isolante_bloqueia_casa_vazia_e_gasta_a_carta() -> None:
    estado = t.nova_partida()
    t.usar_isolante(estado, 0, 2, 0)
    assert estado.casa(2, 0).tipo == t.TipoCasa.BLOQUEIO
    assert "isolante" not in estado.cartas[0]
    assert not estado.erro


def test_isolante_em_casa_ocupada_e_recusado() -> None:
    estado = t.nova_partida()
    t.usar_isolante(estado, 0, 3, 3)
    assert estado.erro
    assert estado.casa(3, 3).tipo == t.TipoCasa.FONTE
    assert "isolante" in estado.cartas[0]


def test_isolante_so_pode_ser_usado_uma_vez() -> None:
    estado = t.nova_partida()
    t.usar_isolante(estado, 0, 2, 0)
    t.usar_isolante(estado, 0, 2, 3)
    assert estado.erro
    assert estado.casa(2, 3).tipo == t.TipoCasa.VAZIA


def test_casa_bloqueada_pelo_isolante_nao_aceita_peca() -> None:
    estado = t.nova_partida()
    t.usar_isolante(estado, 0, 2, 0)
    assert not t.jogar_na_casa(estado, 2, 0)
    assert estado.casa(2, 0).tipo == t.TipoCasa.BLOQUEIO


def test_curto_remove_peca_de_adversario_e_gasta_a_carta() -> None:
    estado = t.nova_partida()
    t.usar_curto(estado, 0, 2, 5)
    assert estado.casa(2, 5).tipo == t.TipoCasa.VAZIA
    assert "curto" not in estado.cartas[0]
    assert not estado.erro


def test_curto_recusa_pecas_protegidas() -> None:
    for linha, coluna in [(2, 2), (1, 6), (0, 6), (3, 3)]:
        estado = t.nova_partida()
        antes = estado.casa(linha, coluna).tipo
        t.usar_curto(estado, 0, linha, coluna)
        assert estado.erro
        assert estado.casa(linha, coluna).tipo == antes
        assert "curto" in estado.cartas[0]


def test_curto_nao_tira_pontos_de_quem_ja_capturou() -> None:
    estado = t.nova_partida()
    pontos_antes = list(estado.pontos)
    t.usar_curto(estado, 0, 2, 5)
    assert (2, 5) not in estado.energizados
    for antes, depois in zip(pontos_antes, estado.pontos, strict=True):
        assert depois >= antes


def test_ponte_liga_o_circuito_por_cima_de_uma_peca_adversaria() -> None:
    estado = t.nova_partida()
    t._colocar(estado, 0, 3, "EW", 1)
    t.usar_ponte(estado, 0, 0, 2, "E")
    assert not estado.erro
    assert estado.casa(0, 3).dono == 1
    assert estado.casa(0, 4).tipo == t.TipoCasa.PECA
    assert estado.casa(0, 4).dono == 0
    assert "ponte" not in estado.cartas[0]
    assert (0, 4) in t.circuito_do_jogador(estado, 0)[0]


def test_ponte_recusa_jogadas_invalidas() -> None:
    for direcao in ["E", "S"]:
        estado = t.nova_partida()
        t.usar_ponte(estado, 0, 0, 2, direcao)
        assert estado.erro
        assert "ponte" in estado.cartas[0]
        assert not estado.pontes
