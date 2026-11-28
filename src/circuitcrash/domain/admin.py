import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime


def ler_valor(texto: str) -> int:
    """Valor do ajuste digitado no formulário: inteiro, com ou sem sinal (+50, -40)."""
    limpo = texto.strip()
    # Só dígitos ASCII: int() sozinho aceitaria "1_000" e dígitos de outros alfabetos.
    if not re.fullmatch(r"[+-]?[0-9]+", limpo):
        raise ValueError("Informe um número inteiro, como 50 ou -20.")
    valor = int(limpo)
    if valor == 0:
        # Um ajuste de 0 não muda o saldo e só sujaria a lista de ações.
        raise ValueError("O valor do ajuste não pode ser zero.")
    return valor


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


@dataclass(frozen=True)
class ResumoAdmin:
    jogadores: int
    partidas: int
    fagulhas_em_circulacao: int


def resumo(saldos: Sequence[int], total_partidas: int) -> ResumoAdmin:
    return ResumoAdmin(
        jogadores=len(saldos),
        partidas=total_partidas,
        fagulhas_em_circulacao=sum(saldos),
    )
