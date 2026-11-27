from dataclasses import dataclass
from datetime import datetime


def ajustar_saldo(saldo_atual: int, valor: int) -> int:
    novo_saldo = saldo_atual + valor
    if novo_saldo < 0:
        raise ValueError("O saldo não pode ficar negativo.")
    return novo_saldo


def eh_admin(nome: str, admin_usuario: str | None) -> bool:
    if not admin_usuario or not admin_usuario.strip():
        return False
    return nome.strip().lower() == admin_usuario.strip().lower()


@dataclass(frozen=True)
class AcaoAdmin:
    admin: str
    jogador: str
    valor: int
    quando: datetime
