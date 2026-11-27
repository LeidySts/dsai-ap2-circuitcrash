def ajustar_saldo(saldo_atual: int, valor: int) -> int:
    novo_saldo = saldo_atual + valor
    if novo_saldo < 0:
        raise ValueError("O saldo não pode ficar negativo.")
    return novo_saldo
