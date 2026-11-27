"""Tabela acoes_admin: historico dos ajustes de Fagulhas feitos pelo administrador.

Revisao: 0002
Anterior: 0001
Criada em: 27/11/2026
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "acoes_admin",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("admin", sa.String(length=40), nullable=False),
        sa.Column("jogador_id", sa.String(length=40), nullable=False),
        sa.Column("valor", sa.Integer(), nullable=False),
        sa.Column("quando", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["jogador_id"],
            ["jogadores.id"],
            name=op.f("fk_acoes_admin_jogador_id_jogadores"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_acoes_admin")),
    )


def downgrade() -> None:
    op.drop_table("acoes_admin")
