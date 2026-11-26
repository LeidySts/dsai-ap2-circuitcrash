from circuitcrash.domain.missoes import Conquista, Missao


def test_missao_avanca_e_conclui():
    missao = Missao(id=1, descricao="Jogar 3 partidas", recompensa_fagulhas=10, meta=3)
    assert not missao.concluida
    missao.avancar(2)
    assert missao.progresso_atual == 2
    assert not missao.concluida
    missao.avancar(1)
    assert missao.concluida


def test_conquista_avanca_e_desbloqueia():
    conquista = Conquista(id=1, titulo="Primeira vitória", meta=1)
    assert not conquista.desbloqueada
    conquista.avancar()
    assert conquista.desbloqueada
