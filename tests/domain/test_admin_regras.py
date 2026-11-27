from datetime import datetime

from circuitcrash.domain.admin import AcaoAdmin, eh_admin


def test_jogador_com_o_nome_do_admin_e_admin() -> None:
    assert eh_admin("leidy", "leidy") is True


def test_outro_jogador_nao_e_admin() -> None:
    assert eh_admin("bia", "leidy") is False


def test_sem_admin_configurado_ninguem_e_admin() -> None:
    assert eh_admin("leidy", None) is False
    assert eh_admin("leidy", "") is False


def test_nome_do_admin_ignora_maiusculas_e_espacos() -> None:
    assert eh_admin(" Leidy ", "leidy") is True


def test_acao_admin_guarda_quem_jogador_valor_e_quando() -> None:
    quando = datetime(2026, 11, 27, 12, 0)
    acao = AcaoAdmin("leidy", "bia", 50, quando)
    assert acao.admin == "leidy"
    assert acao.jogador == "bia"
    assert acao.valor == 50
    assert acao.quando == quando
