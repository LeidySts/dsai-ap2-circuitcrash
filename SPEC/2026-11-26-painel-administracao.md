# Painel de administração

Data: 2026-11-26
Autora: Leidiane Santos dos Santos

## Objetivo

Dar a quem administra o CircuitCrash uma página para acompanhar o jogo e cuidar do que existe nele, sem mexer no banco de dados na mão.

## Requisitos

- FR-001: a página /admin mostra os números do jogo: total de jogadores, total de partidas e total de Fagulhas em circulação.
- FR-002: a página lista os jogadores com nome, rating e saldo de Fagulhas, do maior rating para o menor.
- FR-003: o administrador pode ajustar o saldo de Fagulhas de um jogador, informando o valor; o saldo nunca fica negativo e o valor 0 é recusado, porque não muda nada.
- FR-004: quem não é administrador e abre /admin vê a mensagem "Acesso restrito" e nada mais.
- FR-005: cada ajuste de saldo fica registrado numa lista de ações (quem ajustou, em qual jogador, valor e horário), visível no painel.

## Fora do escopo

- Criar ou apagar contas.
- Login real com senha: nesta versão o administrador é definido por um nome fixo na configuração.

## Decisões provisórias

- O administrador é o jogador cujo nome está na variável de ambiente ADMIN_USUARIO.
- O ajuste soma ou subtrai do saldo atual, em vez de substituí-lo.

## Critérios de aceite

- Um jogador comum recebe "Acesso restrito" em /admin.
- O administrador vê os números e a lista de jogadores.
- Um ajuste de saldo atualiza o jogador e aparece na lista de ações.
- Ajuste que deixaria o saldo negativo é recusado com mensagem clara.
- Ajuste de valor 0 é recusado com mensagem clara e não aparece na lista de ações.