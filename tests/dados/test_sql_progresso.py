import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from circuitcrash.dados.sql import RepositorioSQL, Base
from circuitcrash.domain.missoes import Missao, Conquista
from circuitcrash.domain.progresso import AtualizadorDeMissoes, ResultadoPartida


@pytest.fixture
def repositorio():
    # Cria um banco de dados SQLite em memória para o teste
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    # Mock básico para a sessão funcionar no teste
    repo = RepositorioSQL.__new__(RepositorioSQL)
    repo._sessao = Session()
    repo._hoje = lambda: "2026-11-25" 
    return repo


def test_fluxo_completo_de_progresso(repositorio):
    jogador_id = "luma_dev"
    
    # 1. Criamos a missão e conquista
    missao = Missao(id=1, descricao="Jogar 1 partida", recompensa_fagulhas=10, meta=1)
    conquista = Conquista(id=1, titulo="Primeira vitória", meta=1)
    
    # 2. O cérebro processa a partida
    atualizador = AtualizadorDeMissoes(missoes=[missao], conquistas=[conquista])
    resultado = ResultadoPartida(colocacao=1, fagulhas_ganhas=40, vitorias=1)
    atualizador.processar_partida(resultado)
    
    # 3. O banco de dados salva o progresso real
    repositorio.salvar_progresso(jogador_id, [missao], [conquista])
    
    # 4. Verificamos se a missão foi concluída e a conquista desbloqueada
    assert missao.concluida is True
    assert conquista.desbloqueada is True
