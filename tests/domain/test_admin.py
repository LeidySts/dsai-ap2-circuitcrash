import pytest

from circuitcrash.domain.admin import ajustar_saldo


def test_ajuste_positivo_soma_ao_saldo() -> None:
    assert ajustar_saldo(100, 50) == 150


def test_ajuste_negativo_subtrai_do_saldo() -> None:
    assert ajustar_saldo(100, -30) == 70


def test_ajuste_que_zera_o_saldo_e_aceito() -> None:
    assert ajustar_saldo(100, -100) == 0


def test_ajuste_que_deixaria_saldo_negativo_e_recusado() -> None:
    with pytest.raises(ValueError):
        ajustar_saldo(100, -101)
