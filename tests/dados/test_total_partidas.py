from circuitcrash.dados.repositorio import Repositorio
from circuitcrash.domain.modelos import ResultadoPartida, TipoPartida


def _resultado() -> ResultadoPartida:
    return ResultadoPartida(TipoPartida.CASUAL, 2, 10, 3, 1482, 0, 25, False)


def test_total_partidas_conta_as_partidas_de_exemplo(repo: Repositorio) -> None:
    # Dados de exemplo: 5 partidas do veterano e 2 do novato.
    assert repo.total_partidas() == 7


def test_total_partidas_conta_uma_partida_nova(repo: Repositorio) -> None:
    repo.registrar_partida("veterano", _resultado())
    assert repo.total_partidas() == 8


def test_total_partidas_nao_e_a_soma_das_participacoes(repo: Repositorio) -> None:
    # O campo Jogador.partidas soma participações; o total do jogo é outra coisa.
    soma_dos_jogadores = sum(j.partidas for j in repo.listar_jogadores())
    assert repo.total_partidas() != soma_dos_jogadores
