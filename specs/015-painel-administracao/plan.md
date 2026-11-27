# Plano técnico: Painel de administração

Spec: SPEC/2026-11-26-painel-administracao.md

## Abordagem

Reaproveitar o contrato Repositorio, que já tem listar_jogadores, ranking e obter_jogador. Acrescentar o que falta, nas duas versões (memória e SQL), com os mesmos testes rodando contra as duas.

## Domínio (src/circuitcrash/domain/admin.py, Python puro)

- Resumo do jogo: total de jogadores, total de partidas e total de Fagulhas em circulação.
- ajustar_saldo(saldo_atual, valor): devolve o novo saldo; recusa se ficar negativo.
- AcaoAdmin: quem, jogador, valor e horário; o horário vem de fora, para o teste ser previsível.
- eh_admin(nome, admin_usuario): compara com o nome configurado.

## Dados (src/circuitcrash/dados)

- Contrato Repositorio ganha: ajustar_fagulhas(jogador_id, valor) e acoes_admin().
- Implementação em memória e implementação SQL, com uma tabela nova para as ações (migração Alembic).

## Tela (src/circuitcrash/web e app.py)

- GET /admin: números, lista de jogadores e lista de ações; jogador comum vê Acesso restrito.
- POST /admin/ajuste: recebe jogador e valor, mostra mensagem de sucesso ou erro.
- Template admin.html e estilo em app.css, funcionando em 390 px de largura.

## Configuração

- ADMIN_USUARIO lido do ambiente; no Render, definida no painel do serviço.

## Riscos

- Mexer no contrato Repositorio exige atualizar as duas implementações juntas.
- Sem login real, a proteção é só por nome; fica registrado como limitação.