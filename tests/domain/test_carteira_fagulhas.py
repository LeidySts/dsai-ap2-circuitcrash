from circuitcrash.domain.economia import LIMITE_DIARIO_FAGULHAS, CarteiraFagulhas


def test_receber_fagulhas_respeitando_limite_diario():
    carteira = CarteiraFagulhas()

    # Tenta ganhar 350 (deve funcionar)
    assert carteira.receber(350) == 350
    assert carteira.saldo == 350
    assert carteira.ganho_hoje == 350

    # Tenta ganhar mais 100, mas o limite é 400. Então só recebe 50.
    assert carteira.receber(100) == 50
    assert carteira.saldo == LIMITE_DIARIO_FAGULHAS
    assert carteira.ganho_hoje == LIMITE_DIARIO_FAGULHAS

    # Tenta ganhar mais, mas já bateu o limite diário (deve retornar 0)
    assert carteira.receber(50) == 0
    assert carteira.saldo == LIMITE_DIARIO_FAGULHAS
