from datetime import datetime

import pytest

from circuitcrash.dados.memoria import RepositorioMemoria
from circuitcrash.domain.admin import AcaoAdmin

QUANDO = datetime(2026, 11, 27, 12, 0)
DEPOIS = datetime(2026, 11, 27, 13, 0)


def test_ajustar_fagulhas_soma_ao_saldo() -> None:
    repo = RepositorioMemoria()
    jogador = repo.listar_jogadores()[0]
    antes = jogador.fagulhas
    novo = repo.ajustar_fagulhas("admin", jogador.id, 50, QUANDO)
    assert novo == antes + 50
    assert repo.obter_jogador(jogador.id).fagulhas == antes + 50


def test_ajustar_fagulhas_recusa_saldo_negativo() -> None:
    repo = RepositorioMemoria()
    jogador = repo.listar_jogadores()[0]
    antes = jogador.fagulhas
    with pytest.raises(ValueError):
        repo.ajustar_fagulhas("admin", jogador.id, -(antes + 1), QUANDO)
    assert repo.obter_jogador(jogador.id).fagulhas == antes
    assert repo.acoes_admin() == []


def test_ajustar_fagulhas_de_jogador_inexistente() -> None:
    repo = RepositorioMemoria()
    with pytest.raises(KeyError):
        repo.ajustar_fagulhas("admin", "nao-existe", 10, QUANDO)


def test_acoes_admin_lista_do_mais_recente_para_o_mais_antigo() -> None:
    repo = RepositorioMemoria()
    jogador = repo.listar_jogadores()[0]
    repo.ajustar_fagulhas("admin", jogador.id, 10, QUANDO)
    repo.ajustar_fagulhas("admin", jogador.id, 5, DEPOIS)
    acoes = repo.acoes_admin()
    assert [a.valor for a in acoes] == [5, 10]
    assert acoes[0] == AcaoAdmin("admin", jogador.id, 5, DEPOIS)
