from dataclasses import dataclass
from datetime import date


@dataclass
class Missao:
    id: int
    descricao: str
    recompensa_fagulhas: int
    meta: int
    progresso_atual: int = 0
    data_expiracao: date | None = None

    @property
    def concluida(self) -> bool:
        return self.progresso_atual >= self.meta

    def avancar(self, quantidade: int = 1) -> None:
        if not self.concluida:
            self.progresso_atual += quantidade


@dataclass
class Conquista:
    id: int
    titulo: str
    meta: int
    progresso_atual: int = 0

    @property
    def desbloqueada(self) -> bool:
        return self.progresso_atual >= self.meta

    def avancar(self, quantidade: int = 1) -> None:
        if not self.desbloqueada:
            self.progresso_atual += quantidade
