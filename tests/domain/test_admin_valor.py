import pytest

from circuitcrash.domain.admin import ler_valor


@pytest.mark.parametrize(("texto", "esperado"), [("50", 50), ("+50", 50), ("-40", -40), (" 7 ", 7)])
def test_ler_valor_aceita_inteiros_com_ou_sem_sinal(texto: str, esperado: int) -> None:
    assert ler_valor(texto) == esperado


@pytest.mark.parametrize("texto", ["", "   ", "abc", "1.5", "1,5", "10a"])
def test_ler_valor_recusa_o_que_nao_e_inteiro(texto: str) -> None:
    with pytest.raises(ValueError, match="Informe um número inteiro"):
        ler_valor(texto)


@pytest.mark.parametrize("texto", ["0", "+0", "-0", "000"])
def test_ler_valor_recusa_zero(texto: str) -> None:
    with pytest.raises(ValueError, match="O valor do ajuste não pode ser zero."):
        ler_valor(texto)
