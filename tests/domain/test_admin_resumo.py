from circuitcrash.domain.admin import ResumoAdmin, resumo


def test_resumo_conta_jogadores_partidas_e_soma_as_fagulhas() -> None:
    assert resumo([100, 50, 0], 7) == ResumoAdmin(jogadores=3, partidas=7, fagulhas_em_circulacao=150)


def test_resumo_sem_jogadores_tudo_zero() -> None:
    assert resumo([], 0) == ResumoAdmin(jogadores=0, partidas=0, fagulhas_em_circulacao=0)
